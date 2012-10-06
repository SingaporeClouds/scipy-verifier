package com.singpath.verifiers;

import bsh.Interpreter;
import bsh.TargetError;
import com.singpath.verifiers.Verifier;
import java.io.ByteArrayOutputStream;
import java.io.PrintStream;
import net.minidev.json.*;
import org.apache.log4j.BasicConfigurator;
import java.io.StringWriter;
import java.io.PrintWriter;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import java.nio.charset.Charset;


public class JavaVerifier extends Verifier{
	
	public JavaVerifier(String ThreadName, ThreadGroup ThreadGroup){
		
		super(ThreadName, ThreadGroup,JavaVerifier.class);
		this.log.info("Java Verifier started");
	}
	
	public void compile_problem(){
		
		ByteArrayOutputStream outputBuffer = new ByteArrayOutputStream();
		PrintStream output = new PrintStream(outputBuffer);
		Interpreter interpreter = new Interpreter(null, output, output, false, null);
		interpreter.setStrictJava(true);
		
		if (this.solution==null || this.tests==null){
			
			this.set_result("{\"errors\": \"No solution or tests defined\"}");
			return;
		}
		
		try
		{
			interpreter.eval("static import org.junit.Assert.*;");
		}
		catch(Exception e)
		{
			StringWriter sw = new StringWriter();
			PrintWriter  pw = new PrintWriter(sw);
			e.printStackTrace(pw);
			String error = sw.toString();
			this.set_result("{\"errors\": \""+error+"\"}");
			this.log.error(error);
			return;
		}
		
		try {
			// Eval the user text
			interpreter.eval(this.solution);
		}
		catch(Exception e)
		{
			StringWriter sw = new StringWriter();
			PrintWriter  pw = new PrintWriter(sw);
			e.printStackTrace(pw);
			String error = sw.toString();
			this.set_result("{\"errors\": \""+error+"\"}");
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
		this.set_result(resultjson.toJSONString());
	return;

	}
		

	public static void main(String[] args)
	
	{ 	
		BasicConfigurator.configure();
		JSONObject dict = new JSONObject();
	
		dict.put("tests", "assertTrue(false);\n assertEquals(b,2);\n assertEquals(a, 1);");
		dict.put("solution", "int a=1;\nint b=1;\n\n");
		
		try
		{

			ThreadGroup VTG = new ThreadGroup("VTG");
			JavaVerifier instance = new JavaVerifier("VTG",VTG);
			System.out.println(instance.process_problem(dict.toString()));
		}
		catch(Exception e)
		{
			e.printStackTrace();
		}


	}

}