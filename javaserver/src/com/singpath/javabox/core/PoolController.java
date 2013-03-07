package com.singpath.javabox.core;

import org.apache.log4j.Logger;

import java.io.DataOutputStream;
import java.io.OutputStream;
import java.io.PrintWriter;
import java.io.StringWriter;
import java.net.Socket;
import java.util.LinkedList;
import java.util.Queue;
import java.util.concurrent.Executors;
import java.util.concurrent.ThreadPoolExecutor;

public class PoolController {

	protected ThreadPoolExecutor threadPool = null;
	protected Queue<WaitItem> Queue = null;
	protected Long QueueMaxTime = (long) 5000;
	protected String QueueMaxTimeError = "{\"errors\":\"Insufficient resources to process your request\"}";
	protected Logger log = null;

	public PoolController(int maxAllowedProcess) {
		this.threadPool = (ThreadPoolExecutor) Executors
				.newFixedThreadPool(maxAllowedProcess);
		this.Queue = new LinkedList<WaitItem>();
		this.log = Logger.getLogger(PooledServer.class);
	}

	public synchronized void execute(Socket client) {

		/*
		 * if (this.Queue.size()==0 &&
		 * (this.threadPool.getActiveCount()<this.threadPool
		 * .getMaximumPoolSize()) ){ //process the request
		 * this.threadPool.execute(new Worker(client));
		 * 
		 * }
		 */

		// put the request in the queue
		WaitItem NewWaitItem = new WaitItem(client, System.currentTimeMillis());
		this.Queue.offer(NewWaitItem);

	}

	/*
	 * add new task to the pool if is possible , and dispatches the item with
	 * max wait time
	 */
	public synchronized void check_queue() {
		// get the current space in the pool
		int space = this.threadPool.getMaximumPoolSize()
				- this.threadPool.getActiveCount();
		// add new task to the pool
		if (space > 0) {
			while (this.Queue.peek() != null) {
				this.threadPool.execute(new Worker(this.Queue.poll()
						.get_client()));
				space--;
				if (space <= 0) {
					break;
				}
			}
		}

		while (this.Queue.peek() != null) {
			if (this.Queue.peek().time_from_request() < this.QueueMaxTime) {
				break;
			}
			// dispatches the item with max wait time
			try {

				Socket clientSocket = this.Queue.poll().get_client();
				OutputStream output = clientSocket.getOutputStream();
				DataOutputStream DataOutput = new DataOutputStream(output);

				DataOutput.writeUTF(this.QueueMaxTimeError);

				clientSocket.close();
				this.log.info("insufficient resources to process new request");

			} catch (Exception e) {
				StringWriter sw = new StringWriter();
				PrintWriter pw = new PrintWriter(sw);
				e.printStackTrace(pw);
				String error = sw.toString();
				this.log.error(error);
			}

		}

	}

	public synchronized void shutdown() {
		this.threadPool.shutdown();
	}

}
