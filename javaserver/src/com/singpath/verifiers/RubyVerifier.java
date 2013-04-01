package com.singpath.verifiers;

import net.minidev.json.JSONObject;
import net.minidev.json.JSONStyle;
import net.minidev.json.JSONValue;
import org.apache.log4j.BasicConfigurator;
import org.jruby.Ruby;
import org.jruby.RubyInstanceConfig;
import org.jruby.RubyRuntimeAdapter;
import org.jruby.javasupport.JavaEmbedUtils;

import java.io.ByteArrayOutputStream;
import java.io.PrintStream;
import java.io.PrintWriter;
import java.io.StringWriter;
import java.util.ArrayList;


public class RubyVerifier extends Verifier {

	public RubyVerifier(String ThreadName, ThreadGroup ThreadGroup) {

		super(ThreadName, ThreadGroup, RubyVerifier.class);
		this.log.info("Ruby Verifier started");
	}

	public void compile_problem() {

		if (this.solution == null || this.tests == null) {

			this.set_result("{\"errors\": \"No solution or tests defined\"}");
			return;
		}

		// Initialize Jruby
		ByteArrayOutputStream outputBuffer = new ByteArrayOutputStream();
		PrintStream output = new PrintStream(outputBuffer);
        JSONObject resultjson = new JSONObject();

		RubyInstanceConfig config = new RubyInstanceConfig();
		config.setOutput(output);
		config.setError(output);

		Ruby runtime = JavaEmbedUtils.initialize(new ArrayList<String>(),
				config);
		RubyRuntimeAdapter evaler = JavaEmbedUtils.newRuntimeAdapter();

		String[] solutionLines = this.solution.trim().split("\n");
		String[] testscripts = this.tests.trim().split("\n");

		// write the code that will be execute in Jruby runtime
		String Code = "\nrequire 'test/unit'\n";
		Code += "require 'stringio' \n";
		Code += "require 'json' \n";
		Code += "extend Test::Unit::Assertions \n";
		Code += "out = StringIO.new\n";
		Code += "$stdout = out\n";
		Code += "$stderr = out\n";
		Code += "solved=true\n";
		Code += "testResults=[]\n";
        Code += "begin\n";
        Code += "\tbegin\n";
		for (String line : solutionLines) {
			Code += "\t\t" + line + "\n";

		}
        Code += "\trescue Exception => e\n";
        Code += "\t\t$stdout = STDOUT\n";
        Code += "\t\tputs '{\"errors\":\"'+e.message+'\"}'\n";
        Code += "\t\texit\n";
        Code += "\tend\n";
		for (String testscript : testscripts) {
			if (testscript.indexOf("assert") == -1) {
				Code += "\tbegin\n";
				Code += "\t\t" + testscript + "\n";
				Code += "\trescue Exception => e\n";
				Code += "\t\t$stdout = STDOUT\n";
				Code += "\t\tputs '{\"errors\":\"in tests: " + testscript.replace("'","\\'")
						+ " ==> '+e.message+'\"}'\n";
				Code += "\t\texit\n";
				Code += "\tend\n";

			} else {
				Code += "\tbegin\n";
				Code += "\t\t" + testscript + "\n";
				Code += "\t\tresultHash = Hash.new\n";
				Code += "\t\tresultHash['expected'] = ''\n";
				Code += "\t\tresultHash['received'] = ''\n";
				Code += "\t\tresultHash['call']     = '" + testscript.replace("'","\\'") + "'\n";
				Code += "\t\tresultHash['correct']  = true\n";
				Code += "\t\ttestResults.push(resultHash)\n";
				// assertion exeption
				Code += "\trescue MiniTest::Assertion => e\n";
				Code += "\t\t$stdout = STDOUT\n";
				Code += "\t\tsolved=false\n";
				Code += "\t\tresultHash = Hash.new\n";
				Code += "\t\tres=e.message.scan(/<(.*)>/)\n";
				Code += "\t\tresultHash['expected'] = res[0][0]\n";
				Code += "\t\tresultHash['received'] = res[1][0]\n";
				Code += "\t\tresultHash['call']     = '" + testscript.replace("'","\\'") + "'\n";
				Code += "\t\tresultHash['correct']  = false\n";
				Code += "\t\ttestResults.push(resultHash)\n";
				// others exeptions
				Code += "\trescue Exception => e\n";
				Code += "\t\t$stdout = STDOUT\n";
				Code += "\t\tputs '{\"errors\":\"in tests: " + testscript.replace("'","\\'")
						+ " ==> '+e.message+'\"}'\n";
				Code += "\t\texit\n";
				Code += "\tend\n";

			}
		}
		Code += "\t$stdout = STDOUT\n";
		Code += "\tresultjson = Hash.new\n";
		Code += "\tresultjson['solved'] = solved\n";
		Code += "\tresultjson['results'] = testResults\n";
		Code += "\tresultjson['printed'] = out.string\n";
		Code += "\tprint JSON.dump(resultjson)\n";
		Code += "rescue SystemExit\n";
		Code += "end";
        try
        {
            evaler.eval(runtime, Code);
        }
        catch(Exception e)
        {
            StringWriter sw = new StringWriter();
            PrintWriter pw = new PrintWriter(sw);
            e.printStackTrace(pw);
            String error = "Syntax error, please check your code.  "+sw.toString();
            this.log.error(error);
            resultjson.put("errors",error);
            this.set_result(JSONValue.toJSONString(resultjson, JSONStyle.NO_COMPRESS));
            return;
        }
		String result = new String(outputBuffer.toByteArray());
		this.log.error(result);
		this.set_result(result.trim());
		return;
	}

	public static void main(String[] args)

	{
		BasicConfigurator.configure();
		JSONObject dict = new JSONObject();

		dict.put("tests", "assert_equal('testing',solution)");
		dict.put("solution","solution = 'testing'");

		try {

			ThreadGroup VTG = new ThreadGroup("VTG");
			RubyVerifier instance = new RubyVerifier("VTG", VTG);
			System.out.println(instance.process_problem(dict.toString()));
		} catch (Exception e) {
			e.printStackTrace();
		}

	}

}