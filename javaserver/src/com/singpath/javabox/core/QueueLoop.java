package com.singpath.javabox.core;

import org.apache.log4j.Logger;

import java.io.PrintWriter;
import java.io.StringWriter;

public class QueueLoop extends Thread {
	protected PoolController controller = null;
	protected Logger log = null;

	public QueueLoop(PoolController controller) {
		super();
		this.log = Logger.getLogger(PooledServer.class);
		this.controller = controller;
	}

	@Override
	public void run() {
		while (true) {
			this.controller.check_queue();
			try {
				Thread.sleep(200);
			} catch (InterruptedException e) {
				StringWriter sw = new StringWriter();
				PrintWriter pw = new PrintWriter(sw);
				e.printStackTrace(pw);
				String error = sw.toString();
				this.log.error("Unexpected error");
				this.log.error(error);
				throw new RuntimeException("Unexpected error", e);
			}
		}

	}

}
