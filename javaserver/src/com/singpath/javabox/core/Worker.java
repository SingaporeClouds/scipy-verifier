package com.singpath.javabox.core;

import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.InputStream;
import java.io.OutputStream;
import java.io.PrintWriter;
import java.io.StringWriter;
import java.net.Socket;
import java.util.UUID;

import org.apache.log4j.Logger;

import com.singpath.verifiers.JavaVerifier;
import com.singpath.verifiers.RubyVerifier;
import com.singpath.verifiers.Verifier;
import com.singpath.verifiers.JSPVerifier;

public class Worker implements Runnable {
	protected Logger log = null;
	protected Socket clientSocket = null;

	public Worker(Socket clientSocket) {
		this.clientSocket = clientSocket;
		this.log = Logger.getLogger(PooledServer.class);

	}

	protected String process_request(String request) {
		if (request.length() < 10) {
			this.log.error("Bad request");
			return "{\"errors\":\"Bad request\"}";
		} else {
			String route = request.substring(0, 10).trim();
			String msg = request.substring(10).trim();
			String uuid = UUID.randomUUID().toString();
			try {
				ThreadGroup safeThreadGroup = new ThreadGroup(uuid);
				Verifier instance = null;
				
				if (route.equals("java")) {
					instance = new JavaVerifier(uuid,
							safeThreadGroup);
				}
				
				if (route.equals("ruby")) {

					instance = new RubyVerifier(uuid,
							safeThreadGroup);
				}
				
				if (route.equals("jsp")) {
					instance = new JSPVerifier(uuid,
							safeThreadGroup);
				}
				if(!instance.equals(null)){
					return instance.process_problem(msg);
				}

			} catch (Exception e) {
				StringWriter sw = new StringWriter();
				PrintWriter pw = new PrintWriter(sw);
				e.printStackTrace(pw);
				String error = sw.toString();
				this.log.error(error);
				return "{\"errors\":\"Internal Server Error\"}";
			}

			this.log.error("Verifier " + route + " don't exist");
			return "{\"errors\":\"Verifier " + route + " don't exist\"}";

		}

	}

	@Override
	public void run() {
		try {
			InputStream input = clientSocket.getInputStream();
			OutputStream output = clientSocket.getOutputStream();

			DataInputStream DataInput = new DataInputStream(input);
			DataOutputStream DataOutput = new DataOutputStream(output);
			String request = DataInput.readUTF();
			DataOutput.writeUTF(this.process_request(request));

			this.clientSocket.close();
			this.log.info("Request processed successfully");

		} catch (Exception e) {
			StringWriter sw = new StringWriter();
			PrintWriter pw = new PrintWriter(sw);
			e.printStackTrace(pw);
			String error = sw.toString();
			this.log.error(error);
			try {
				clientSocket.close();
			} catch (Exception ne) {
			}
		}
	}
}
