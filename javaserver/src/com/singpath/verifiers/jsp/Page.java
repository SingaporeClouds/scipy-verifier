package com.singpath.verifiers.jsp;

import org.apache.http.HttpResponse;
import org.apache.http.NameValuePair;
import org.apache.http.client.HttpClient;
import org.apache.http.client.entity.UrlEncodedFormEntity;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.client.utils.URLEncodedUtils;
import org.apache.http.impl.client.DefaultHttpClient;
import org.apache.http.message.BasicNameValuePair;
import org.jsoup.Jsoup;
import org.jsoup.nodes.Document;

import java.io.BufferedReader;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;

public class Page {

	protected String url;

	public Page(String url) {
		this.url = url;
	}

	// convert inputstream to String
	public String is_to_s(InputStream is) throws Throwable {

		// read it with BufferedReader
		BufferedReader br = new BufferedReader(new InputStreamReader(is));

		StringBuilder sb = new StringBuilder();

		String line;

		while ((line = br.readLine()) != null) {
			sb.append(line);
		}

		br.close();

		return sb.toString();
	}

	private Document do_post(Map<String, String> params) throws Throwable {

		HttpResponse response = null;

		// Instantiate an HttpClient
		HttpClient client = new DefaultHttpClient();

		// Instantiate a POST HTTP method
		HttpPost method = new HttpPost(url);

		// add params
		ArrayList<NameValuePair> apacheParams = new ArrayList<NameValuePair>();

		for (String sub_params : params.keySet()) {
			apacheParams.add(new BasicNameValuePair((String) sub_params,
					(String) params.get(sub_params)));
		}

		method.setEntity(new UrlEncodedFormEntity(apacheParams));

		try {
			response = client.execute(method);
		} catch (Throwable e) {
			throw new Throwable();
		}

		int statusCode = response.getStatusLine().getStatusCode();

		if (statusCode != 200) {
			String responseBody = this.is_to_s(response.getEntity()
					.getContent());
			Document responseDocument = Jsoup.parse(responseBody);
			String Error = responseDocument.select("pre").text();
			// get error
			throw new JspException(Error);
		}

		// When HttpClient instance is no longer needed,
		// shut down the connection manager to ensure
		// immediate deallocation of all system resources
		String responseBody = this.is_to_s(response.getEntity().getContent());
		client.getConnectionManager().shutdown();
		return Jsoup.parse(responseBody);
	}

	public Document post() throws Throwable {

		return this.do_post(new HashMap<String, String>());
	}

	public Document post(String arg0, String arg1) throws Throwable {
		HashMap<String, String> args = new HashMap<String, String>();
		args.put(arg0, arg1);
		return this.do_post(args);
	}

	public Document post(HashMap<String, String> args) throws Throwable {
		return this.do_post(args);
	}

	private Document do_get(Map<String, String> params) throws Throwable {
		HttpResponse response = null;

		// Instantiate an HttpClient
		HttpClient client = new DefaultHttpClient();

		

		// add params
		ArrayList<NameValuePair> apacheParams = new ArrayList<NameValuePair>();

		for (String sub_params : params.keySet()) {
			apacheParams.add(new BasicNameValuePair((String) sub_params,
					(String) params.get(sub_params)));
		}
		// Instantiate a POST HTTP method
		HttpGet method = new HttpGet(url+"?"+URLEncodedUtils.format(apacheParams,"UTF-8"));

		try {
			response = client.execute(method);
		} catch (Throwable e) {
			throw new Throwable();
		}

		int statusCode = response.getStatusLine().getStatusCode();

		if (statusCode != 200) {
			String responseBody = this.is_to_s(response.getEntity()
					.getContent());
			Document responseDocument = Jsoup.parse(responseBody);
			String Error = responseDocument.select("pre").text();
			// get error
			throw new JspException(Error);
		}

		// When HttpClient instance is no longer needed,
		// shut down the connection manager to ensure
		// immediate deallocation of all system resources
		String responseBody = this.is_to_s(response.getEntity().getContent());
		client.getConnectionManager().shutdown();
		return Jsoup.parse(responseBody);
	}

	public Document get() throws Throwable {

		return this.do_get(new HashMap<String, String>());
	}

	public Document get(String arg0, String arg1) throws Throwable {
		HashMap<String, String> args = new HashMap<String, String>();
		args.put(arg0, arg1);
		return this.do_get(args);
	}

	public Document get(HashMap<String, String> args) throws Throwable {
		return this.do_get(args);
	}

	public static void main(String[] args) {
		Page tester = new Page(
				"http://127.0.0.1:8080/b4f94c64-bd56-48de-8f6a-214f72b43419.jsp");
		Document response = null;
		try {
			response = tester.get("fruit", "guava");
		} catch (JspException e) {
			// TODO Auto-generated catch block
			System.out.println(e.getMessage());
			return;

		} catch (Throwable e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
			return;

		}
		System.out.println(response.html());

	}

}
