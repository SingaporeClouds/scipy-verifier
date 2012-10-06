package com.singpath.verifiers;

import java.io.PrintWriter;
import java.io.StringWriter;

import net.minidev.json.JSONObject;
import net.minidev.json.JSONValue;

import org.apache.log4j.Logger;

public abstract class Verifier extends Thread {

	protected ThreadGroup mainThread;
	protected String result;
	protected String solution;
	protected String tests;
	protected Logger log;
	protected int maxExecutionTime = 5000;

	/*
	 * Super constructor
	 */
	public Verifier(String ThreadName, ThreadGroup ThreadGroup, Class LogName) {
		super(ThreadGroup, ThreadName);
		this.mainThread = ThreadGroup;
		this.log = Logger.getLogger(LogName);
	}

	/*
	 * compile the solution and tests, must write the result as encode json
	 * object in the result variable
	 */
	abstract void compile_problem();

	@Override
	public void run() {
		// execute verifier procedure
		this.compile_problem();
	}

	protected synchronized void set_result(String r) {
		this.result = r;
	}

	protected synchronized String get_result() {
		return this.result;

	}

	public String process_problem(String jsonrequest) {

		String ret;

		try {
			// Load jsonrequest object
			Object obj = JSONValue.parseStrict(jsonrequest);
			JSONObject dict = (JSONObject) obj;

			this.solution = (String) dict.get("solution");
			this.tests = (String) dict.get("tests");
			// start
			try {

				this.start();
				this.join(this.maxExecutionTime);
				if (this.mainThread != null) {
					this.mainThread.stop();
				}

				if (this.get_result() == null) {
					ret = "{\"errors\": \"Your code took too long to return. Your solution may be stuck in an infinite loop. Please try again.\"}";
					this.log.error("code take much time to run");
				} else {
					ret = this.get_result();
				}

			} catch (Exception e) {
				StringWriter sw = new StringWriter();
				PrintWriter pw = new PrintWriter(sw);
				e.printStackTrace(pw);
				String error = sw.toString();
				ret = "{\"errors\": \"Internal server error (see log)\"}";
				this.log.error(error);
			}
		} catch (Exception e) {

			ret = "{\"errors\": \"Bad request\"}";
			this.log.error("Bad request");

		}

		return ret;

	}

}