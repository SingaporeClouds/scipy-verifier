package com.singpath.verifiers;

import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.PrintStream;
import java.io.PrintWriter;
import java.io.StringWriter;
import java.util.UUID;

import net.minidev.json.JSONObject;

import org.apache.commons.io.FileUtils;
import org.apache.log4j.BasicConfigurator;

import bsh.Interpreter;

public class JSPVerifier extends Verifier {

	protected String JSPTester;

	public JSPVerifier(String ThreadName, ThreadGroup ThreadGroup,
			String testercode) {

		super(ThreadName, ThreadGroup, JSPVerifier.class);
		this.log.info("JSP Verifier started");
		this.JSPTester = testercode;
	}

	@Override
	public void compile_problem() {

		ByteArrayOutputStream outputBuffer = new ByteArrayOutputStream();
		PrintStream output = new PrintStream(outputBuffer);
		Interpreter interpreter = new Interpreter(null, output, output, false,
				null);
		interpreter.setStrictJava(false);

		if (this.solution == null || this.tests == null) {

			this.set_result("{\"errors\": \"No solution or tests defined\"}");
			return;
		}

		// save solution in a file
		String uuid  = UUID.randomUUID().toString();
		File file = new File(uuid);
		
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
		
		this.JSPTester = this.JSPTester.replaceAll("%filename%", "/" + file.getPath());
		try {
			interpreter.eval(this.JSPTester);
		}

		catch (Exception e) {
			StringWriter sw = new StringWriter();
			PrintWriter pw = new PrintWriter(sw);
			e.printStackTrace(pw);
			String error = sw.toString();
			this.set_result("{\"errors\": \"" + error + "\"}");
			this.log.error(error);
			return;
		}
		this.log.error("nothing");

		// this.set_result(resultjson.toString());
		return;

	}

	public static void main(String[] args)

	{
		BasicConfigurator.configure();
		JSONObject dict = new JSONObject();

		dict.put("tests",
				"assertTrue(false);\n assertEquals(b,2);\n assertEquals(a, 1);");
		dict.put("solution", "<%@ page import=\"java.util.*, java.text.*\" %>"+
"<HTML><HEAD><TITLE>Hello Pineapples</TITLE></HEAD><BODY>	<H1>Hello World</H1><TABLE>	<TR><TD><P>This is an <B>embedded</B> table</P>"+
			"</TD></TR><TR><TD>The request parameter 'fruit' has a value of <%= request.getParameter(\"fruit\") %>"+
			"</TD></TR></TABLE>Today is: <%= new SimpleDateFormat(\"dd/MM/yyyy\").format(new Date()) %></BODY></HTML>");

		File file = new File(
				"/home/cristian/workspace/javaserver/src/com/singpath/utils/JSPTester.java");

		try {

			ThreadGroup VTG = new ThreadGroup("VTG");
			String jsptester = FileUtils.readFileToString(file, "utf-8");
			JSPVerifier instance = new JSPVerifier("VTG", VTG, jsptester);
			System.out.println(instance.process_problem(dict.toString()));
		} catch (Exception e) {
			e.printStackTrace();
		}

	}

}
