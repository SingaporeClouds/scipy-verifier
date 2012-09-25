package com.singpath.javabox.core;

import java.io.IOException;
import java.io.PrintWriter;
import java.io.StringWriter;
import java.net.ServerSocket;
import java.net.Socket;

import org.apache.log4j.Logger;

public class PooledServer extends Thread {

	protected int serverPort = 8080;
	protected ServerSocket serverSocket = null;
	protected boolean isStopped = false;
	protected PoolController controller = null;
	protected Logger log = null;

	public PooledServer(int port, PoolController controller) {
		super();
		this.serverPort = port;
		this.controller = controller;
		this.log = Logger.getLogger(PooledServer.class);
	}

	@Override
	public void run() {

		this.openServerSocket();

		this.log.info("Server opened in port  " + this.serverPort);

		while (!this.isStopped()) {

			Socket clientSocket = null;

			try {
				clientSocket = this.serverSocket.accept();
			} catch (IOException e) {
				if (isStopped()) {
					this.log.info("Server stoped");
					return;
				}

				StringWriter sw = new StringWriter();
				PrintWriter pw = new PrintWriter(sw);
				e.printStackTrace(pw);
				String error = sw.toString();
				this.log.error("Error accepting client connection");
				this.log.error(error);
				throw new RuntimeException("Error accepting client connection",
						e);
			}

			this.controller.execute(clientSocket);
		}

		this.controller.shutdown();

		this.log.info("Server stoped");
	}

	private synchronized boolean isStopped() {
		return this.isStopped;
	}

	public synchronized void close() {
		this.isStopped = true;
		try {
			this.serverSocket.close();
		} catch (IOException e) {
			StringWriter sw = new StringWriter();
			PrintWriter pw = new PrintWriter(sw);
			e.printStackTrace(pw);
			String error = sw.toString();
			this.log.error("Error closing server");
			this.log.error(error);
			System.exit(0);
			// throw new RuntimeException("Error closing server", e);

		}
	}

	private void openServerSocket() {
		try {
			this.serverSocket = new ServerSocket(this.serverPort);
		} catch (Exception e) {
			StringWriter sw = new StringWriter();
			PrintWriter pw = new PrintWriter(sw);
			e.printStackTrace(pw);
			String error = sw.toString();
			this.log.error("Cannot open port " + this.serverPort);
			this.log.error(error);
			System.exit(0);
			// throw new RuntimeException("Cannot open port "+this.serverPort,
			// e);
		}
	}
}