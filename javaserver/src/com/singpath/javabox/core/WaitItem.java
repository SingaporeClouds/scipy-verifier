package com.singpath.javabox.core;

import java.net.Socket;

/*
 * store a socket connection with a time counter
 */

public class WaitItem {

	private long request_time;
	private Socket client;

	public WaitItem(Socket connection, long request_time) {
		this.request_time = request_time;
		this.client = connection;
	}

	public Socket get_client() {
		return this.client;
	}

	public long time_from_request() {
		return System.currentTimeMillis() - this.request_time;
	}

}
