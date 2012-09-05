import java.io.File;
import java.io.FileNotFoundException;
import java.io.PrintWriter;
import java.io.Writer;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Random;

import net.sf.jsptest.HtmlTestCase;

import org.apache.log4j.Logger;
import org.junit.After;
import org.junit.Before;

import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * This class is not thread safe.  Do not attempt to run methods on it concurrently.
 * 
 * @author masotime
 */
public abstract class JSPTester extends HtmlTestCase {
	
	protected static final Random generator = new Random();
	private File f;
	private Logger logger = Logger.getLogger(this.getClass());
	private boolean isRandomFile = false;
	public static final Pattern p = Pattern.compile("<([^>]*)>");
	
	/**
	 * Create a tester to test against code supplied via the constructor
	 * 
	 * @param code
	 * @throws Exception
	 */
	public JSPTester(String code) throws Exception {
		// manually create the file
		logger.info("Creating JSP file from code: " + code);
		createJSP(code);
		isRandomFile = true;
	}
	
	/**
	 * Create a tester to test against a file that already exists in the filesystem
	 * 
	 * @param f
	 * @throws Exception
	 */
	public JSPTester(File f) throws Exception {
		if (!f.exists()) {
			logger.error("Attempt to run the JSP tester against a non-existent file "+f.getName());
			throw new RuntimeException("Internal Error: Invalid file specified");
		}
		
		this.f = f;
	}
	
	
	/**
	 * Returns a hopefully not-yet-created JSP filename
	 * 
	 * @return
	 */
	private String getRandomJSPName() {
		int nextNum = generator.nextInt(1000000);
		return "test" + nextNum + ".jsp";
	}
	
	/**
	 * Manually creates a JSP file
	 * 
	 * @param code
	 */
	private void createJSP(String code) {
		try {
			
			boolean fileCreated = false;
			do {
				f = new File(getRandomJSPName());
				fileCreated = f.createNewFile();
			} while (!fileCreated);
			
			logger.info("Using randomly generated filename " + f.getName());
			
			Writer w = new PrintWriter(f);
			w.write(code);
			w.close();
		} catch (Exception ex) {
			logger.error("Exception occurred while trying to create a JSP file", ex);
			throw new RuntimeException("Internal Error: Creating JSP file");
		}
	}

	@Before
	public void setUp() throws Exception {
		super.setUp();
	}

	@After
	public void tearDown() throws Exception {
		// clean up
		if (isRandomFile) {
			logger.info("Deleting generated JSP file " + f.getName());
			f.delete();
		}
		super.tearDown();
	}
	
	protected abstract void setParameters();	
	protected abstract void makeAssertions() throws Exception;
	
	public void build() throws Exception {
		
		setUp();		
		setParameters();
		
		// simulate request
		String requestURL = "/" + f.getName();
		String requestMethod = "GET";
		
		logger.info("Attempting to "+requestMethod+" "+requestURL);
		request(requestURL, requestMethod);
		logger.info("Result of JSP request is: " + getRenderedResponse());
		
		makeAssertions();		
		tearDown(); // important!		

	}
	
	public JSPTester onRequest(String key, String value) throws Exception {
		setRequestParameter(key, value);
		request("/" + f.getName(), "GET");
		return this;
	}
	
	public JSPTester and(String key, String value) throws Exception {
		return onRequest(key, value);
	}

	private String errorMsg;
	public void beginTest() { errorMsg = null; };
	public void setErrorMsg(String errorMsg) { this.errorMsg = errorMsg; }
	public void formatTestResult(String assertion) {
		System.out.println("call: "+assertion);
		System.out.println("correct: "+(errorMsg == null));
		
		// attempt to parse the assertion
		String expected = "";
		String received = "";
		if (errorMsg != null && errorMsg.toLowerCase().contains("expected")) {
			Matcher m = p.matcher(errorMsg);
			if (m.find()) {
				expected = m.group(1);
				if (m.find()) received = m.group(1);
			}
		}
		System.out.println("expected: "+expected);
		System.out.println("received: "+received);
		
	}
	
	/**
	 * @param args
	 * @throws FileNotFoundException 
	 */
	public static void main(String[] args) throws FileNotFoundException {
		
		if (args.length != 1) {
			System.err.println("Cannot work if a file is not specified in the arguments.  *Exactly* one argument only please.");
			System.exit(1);
		}
		
		File f = new File(args[0]);
		
		try {
			// create a new tester
			JSPTester tester = new JSPTester(f) {

				@Override
				protected void setParameters() {
					// Put code to set parameters here
					%(parameters)s
				}

				@Override
				protected void makeAssertions() throws Exception {
					// Put code for assertions here
					%(assertions)s
				}
				
			};
			
			// build the tester
			tester.build();
			
		} catch (Exception ex) {
			ex.printStackTrace();
		}

	}

}
