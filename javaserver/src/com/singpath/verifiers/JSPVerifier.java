package com.singpath.verifiers;

import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.PrintStream;
import java.io.PrintWriter;
import java.io.StringWriter;
import java.nio.charset.Charset;
import java.util.UUID;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import net.minidev.json.JSONArray;
import net.minidev.json.JSONObject;

import org.apache.commons.io.FileUtils;
import org.apache.log4j.BasicConfigurator;

import bsh.Interpreter;
import bsh.TargetError;
import com.singpath.verifiers.jsp.JspException;


public class JSPVerifier extends Verifier {


	protected String EvalPage;
	protected String TomcatPath = "/home/verifiers/javaserver/jsp/tomcat/webapps/ROOT/";

	public JSPVerifier(String ThreadName, ThreadGroup ThreadGroup) {

		super(ThreadName, ThreadGroup, JSPVerifier.class);
		this.log.info("JSP Verifier started");
		//this.EvalPage = EvalPage;
	}

	@Override
	public void compile_problem() {

		if (this.solution == null || this.tests == null) {

			this.set_result("{\"errors\": \"No solution or tests defined\"}");
			return;
		}
		ByteArrayOutputStream outputBuffer = new ByteArrayOutputStream();
		PrintStream output = new PrintStream(outputBuffer);
		Interpreter interpreter = new Interpreter(null, output, output, false, null);
		interpreter.setStrictJava(true);
		
		// save solution in a file
		String uuid  = UUID.randomUUID().toString();
		
		File file = new File(this.TomcatPath+uuid+".jsp");
		
		try {
			FileUtils.writeStringToFile(file, this.solution);
		}
		catch (Exception e) {
			StringWriter sw = new StringWriter();
			PrintWriter pw = new PrintWriter(sw);
			e.printStackTrace(pw);
			String error = sw.toString();
			this.set_result("{\"errors\": \"Internal Server Error\"}");
			this.log.error(error);
			return;
		}
		
		
		try {
		//import  Page in beanshell 
		interpreter.eval("import com.singpath.verifiers.jsp.Page");
		//junit
		interpreter.eval("static import org.junit.Assert.*;");
		//jsoup
		interpreter.eval("import org.jsoup.*;\nimport org.jsoup.nodes.*;");
		interpreter.eval("import java.util.*;\nimport java.text.*;");
		String url = "http://127.0.0.1:8080/"+uuid+".jsp";
		interpreter.eval("Page page = new Page(\""+url+"\");");
		}
		catch (Exception e) {
			StringWriter sw = new StringWriter();
			PrintWriter pw = new PrintWriter(sw);
			e.printStackTrace(pw);
			String error = sw.toString();
			this.set_result("{\"errors\": \"Internal Server Error\"}");
			this.log.error(error);
			return;
		}
		String[] testscripts = this.tests.split("\n");
		JSONArray testResults = new JSONArray();
		boolean solved = true;
		
		for(String testscript : testscripts)
		{
			//ignore blank line
			if(testscript.trim().equals(""))
				continue;
			try
			{
				interpreter.eval(testscript);
				if(testscript.indexOf("assert") == -1)
					continue;
			}
			catch(TargetError e)
			{	
				//if there exist a error in the jsp page
				if(e.getTarget().getClass().equals(JspException.class)){
					String error = e.getTarget().getMessage();
					this.set_result("{\"errors\": \""+error+"\"}");
					this.log.error(error);
					return;
					
				}
				//if the error is not a assertion
				if(!e.getTarget().getClass().equals(java.lang.AssertionError.class)){
					StringWriter sw = new StringWriter();
					PrintWriter  pw = new PrintWriter(sw);
					e.getTarget().printStackTrace(pw);
					String error = sw.toString();
					this.set_result("{\"errors\": \""+error+"\"}");
					this.log.error(error);
					return;	
				}
				
				
				JSONObject resulthash = new JSONObject();
				solved = false;
				//special handling for assertTrue and assertFalse, because the exception message is empty
				if(testscript.indexOf("assertTrue(") != -1)
				{
					resulthash.put("expected", true);
					resulthash.put("received", false);
					resulthash.put("call", testscript);
					resulthash.put("correct", false);
					testResults.add(new JSONObject(resulthash));
					continue;
					
				}
				else if(testscript.indexOf("assertFalse(") != -1)
				{
					resulthash.put("expected", false);
					resulthash.put("received", true);
					resulthash.put("call", testscript);
					resulthash.put("correct", false);
					testResults.add(new JSONObject(resulthash));
					continue;
				}
				
				String failS = e.getTarget().getMessage();
				
				// Compile and use regular expression to find the expected and received values
				String patternStr = "^expected:<(.*)> but was:<(.*)>$";
				Pattern pattern = Pattern.compile(patternStr);
				Matcher matcher = pattern.matcher(failS);
				if (matcher.find()) {
					resulthash.put("expected", matcher.group(1));
					resulthash.put("received", matcher.group(2));
					resulthash.put("call", testscript);
					resulthash.put("correct", false);
				} else { //if the regular expression fails, use the old method
					failS = failS.replace("expected:<", "");
					failS = failS.replace("> but was:<", ",");
					failS = failS.replace(">", "");
					String[] ss = failS.split(",");
					resulthash.put("expected", ss[0]);
					resulthash.put("received", ss[1]);
					resulthash.put("call", testscript);
					resulthash.put("correct", false);
				}
				testResults.add(new JSONObject(resulthash));
				continue;
				
			}
			catch(Exception e)
			{
				//if the error is not a assertion
				StringWriter sw = new StringWriter();
				PrintWriter  pw = new PrintWriter(sw);
				e.printStackTrace(pw);
				String error = sw.toString();
				this.set_result("{\"errors\": \""+error+"\"}");
				this.log.error(error);
				return;
			}
			
			JSONObject resulthash = new JSONObject();
			resulthash.put("call", testscript);
			resulthash.put("correct", true);
			testResults.add(new JSONObject(resulthash));	
		}
		
		JSONObject resultjson = new JSONObject();
		resultjson.put("solved", solved);
		resultjson.put("results", testResults);
		resultjson.put("printed", new String(outputBuffer.toByteArray(), Charset.forName("UTF-8")));
		this.set_result(resultjson.toString());
		return;
		
	}

	public static void main(String[] args)

	{
		BasicConfigurator.configure();
		JSONObject dict = new JSONObject();

		dict.put("tests",
				"String expectedDate = new SimpleDateFormat(\"dd/MM/yyyy\").format(new Date());Document response = page.post();\nassertEquals(false,response.html().indexOf(\"Hello Pineapples\") == -1);assertEquals(false,response.html().indexOf(\"T2oday is: \"+expectedDate)==-1);");
		dict.put("solution", "<%@ page import=\"java.util.*, java.text.*\" %>"+
"<HTML><HEAD><TITLE>Hello Pineapples</TITLE></HEAD><BODY>	<H1>Hello World</H1><TABLE>	<TR><TD><P>This is an <B>embedded</B> table</P>"+
			"</TD></TR><TR><TD>The request parameter 'fruit' has a value of <%= request.getParameter(\"fruit\") %>"+
			"</TD></TR></TABLE>Today is: <%= new SimpleDateFormat(\"dd/MM/yyyy\").format(new Date()) %></BODY></HTML>");

		File file = new File(
				"/home/verifiers/javaserver/src/com/singpath/utils/JSPTester.java");

		try {

			ThreadGroup VTG = new ThreadGroup("VTG");
			//String EvalPage = FileUtils.readFileToString(file, "utf-8");
			JSPVerifier instance = new JSPVerifier("VTG", VTG);
			System.out.println(instance.process_problem(dict.toString()));
		} catch (Exception e) {
			e.printStackTrace();
		}

	}

}
