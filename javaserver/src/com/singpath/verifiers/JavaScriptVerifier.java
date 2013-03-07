package com.singpath.verifiers;

import net.minidev.json.JSONArray;
import net.minidev.json.JSONObject;
import net.minidev.json.JSONStyle;
import net.minidev.json.JSONValue;
import org.apache.log4j.BasicConfigurator;
import org.mozilla.javascript.Context;
import org.mozilla.javascript.JavaScriptException;
import org.mozilla.javascript.NativeObject;
import org.mozilla.javascript.Scriptable;

import java.io.FileReader;
import java.io.PrintWriter;
import java.io.StringWriter;


public class JavaScriptVerifier extends Verifier{

    public JavaScriptVerifier(String ThreadName, ThreadGroup ThreadGroup) {

        super(ThreadName, ThreadGroup, JavaScriptVerifier.class);
        this.log.info("JavaScript Verifier started");
    }
    public void compile_problem(){

        JSONObject resultjson = new JSONObject();
        Context cx = Context.enter();
        Scriptable scope = cx.initStandardObjects();
        cx.setOptimizationLevel(-1);

        if (this.solution==null || this.tests==null){
            resultjson.put("errors", "No solution or tests defined");
            this.set_result(JSONValue.toJSONString(resultjson,JSONStyle.NO_COMPRESS));
            return;
        }


        try
        {
            cx.evaluateReader(scope, new FileReader("/home/verifiers/javaserver/js/env.rhino.js"), "env.rhino.js", 0, null);
            cx.evaluateReader(scope, new FileReader("/home/verifiers/javaserver/js/assert_equal.js"), "assert_equal.js", 0, null);

        }
        catch(Exception e)
        {
            StringWriter sw = new StringWriter();
            PrintWriter  pw = new PrintWriter(sw);
            e.printStackTrace(pw);
            String error = sw.toString();
            resultjson.put("errors", error);
            this.set_result(JSONValue.toJSONString(resultjson,JSONStyle.NO_COMPRESS));
            this.log.error(error);
            return;
        }


        try
        {
            cx.evaluateString(scope, this.solution, "solution", 0, null);
        }
        catch(Exception e)
        {
            StringWriter sw = new StringWriter();
            PrintWriter  pw = new PrintWriter(sw);
            e.printStackTrace(pw);
            String error = sw.toString();
            resultjson.put("errors", error);
            this.set_result(JSONValue.toJSONString(resultjson,JSONStyle.NO_COMPRESS));
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
                cx.evaluateString(scope, testscript, "tests", 0, null);
                if(testscript.indexOf("assert") == -1)
                    continue;
            }
            catch(JavaScriptException e)
            {
                JSONObject resulthash = new JSONObject();
                solved = false;
                // check that we get a {exp, act} js object thrown
                if (!(e.getValue() instanceof NativeObject)){
                    StringWriter sw = new StringWriter();
                    PrintWriter  pw = new PrintWriter(sw);
                    e.printStackTrace(pw);
                    String error = sw.toString();
                    resultjson.put("errors", error);
                    this.set_result(JSONValue.toJSONString(resultjson,JSONStyle.NO_COMPRESS));
                    this.log.error(error);
                    return;
                }
                NativeObject assert_err = (NativeObject) e.getValue();
                if (!assert_err.has("exp", null) || !assert_err.has("act", null)){
                    StringWriter sw = new StringWriter();
                    PrintWriter  pw = new PrintWriter(sw);
                    e.printStackTrace(pw);
                    String error = sw.toString();
                    resultjson.put("errors", error);
                    this.set_result(JSONValue.toJSONString(resultjson,JSONStyle.NO_COMPRESS));
                    this.log.error(error);
                    return;
                }

                resulthash.put("expected", assert_err.get("exp", null));
                resulthash.put("received", assert_err.get("act", null));
                resulthash.put("call", testscript);
                resulthash.put("correct", false);
                testResults.add(new JSONObject(resulthash));
                continue;
            }
            catch(Exception e)
            {
                StringWriter sw = new StringWriter();
                PrintWriter  pw = new PrintWriter(sw);
                e.printStackTrace(pw);
                String error = sw.toString();
                resultjson.put("errors", error);
                this.set_result(JSONValue.toJSONString(resultjson,JSONStyle.NO_COMPRESS));
                this.log.error(error);
                return;
            }
            JSONObject resulthash = new JSONObject();
            resulthash.put("call", testscript);
            resulthash.put("correct", true);
            testResults.add(new JSONObject(resulthash));
        }

        resultjson.put("solved", solved);
        resultjson.put("results", testResults);
        this.set_result(resultjson.toJSONString());
        return;
    }

    public static void main(String[] args)

    {
        BasicConfigurator.configure();
        JSONObject dict = new JSONObject();

        dict.put("tests", "assert_equal(1,a);\nassert_equal(2,b);");
        dict.put("solution", "a=1;\nb=2;");

        try
        {

            ThreadGroup VTG = new ThreadGroup("VTG");
            JavaScriptVerifier instance = new JavaScriptVerifier("VTG",VTG);
            System.out.println(instance.process_problem(dict.toString()));
        }
        catch(Exception e)
        {
            e.printStackTrace();
        }


    }



}
