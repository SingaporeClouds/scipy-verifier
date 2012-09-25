import com.singpath.util.Base64;

import org.vertx.java.core.Handler;
import org.vertx.java.core.http.HttpServerRequest;
import org.vertx.java.deploy.Verticle;
import org.vertx.java.core.SimpleHandler;
import org.vertx.java.core.buffer.Buffer;
import org.apache.log4j.Logger;


import java.util.Map;
import java.util.HashMap;
import java.net.URLDecoder;



public class Server extends Verticle {
	
	public Map <String,Object> routes = new HashMap<String,Object>();
	static Logger logger = Logger.getLogger(Server.class);

    public void start() {
	    	
    		//************************Create routes**********************************
    		routes.put("java","java");
    		routes.put("jsp","jsp");
    		//***********************************************************************
    		
        	vertx.createHttpServer().requestHandler(new Handler<HttpServerRequest>() {
        		
            public void handle(final HttpServerRequest req) {
            	
            	final Map <String,String> data;
            	final Buffer body;
            	
            	
            	//check if the verifier exist 
            	if( ! routes.containsKey(req.path) ){
            		req.response.putHeader("content-type", "text/plain");
            		req.response.statusCode    = 404;
            		req.response.statusMessage = "Verifier not found";
            		req.response.end("{\"errors\":\"Verifier not found\"}");
            		logger.error("Verifier not found");
            		return;
            	}
            	
            	
            	//obtain query params with GET or POST method
            	
            	if (req.method.equals("GET")){
            		
            		data  =  req.params();
            		Verify(req,data);
            	}
            	
            	
            	else if (req.method.equals("POST")){
            	
            		body = new Buffer(0);
            		data = new HashMap <String,String> ();
            		
            		req.dataHandler(new Handler<Buffer>() {
            		    public void handle(Buffer buffer) {
            		        body.appendBuffer(buffer);
            		    }
            		});
            		
            		req.endHandler(new SimpleHandler() {
            		    @SuppressWarnings("deprecation")
						public void handle() {
            		      // The entire body has now been received
            		      String items [] = body.toString("UTF-8").split("&");
            		      String key_val[];
            		      for (String i : items) {
            		    	   key_val = i.split("=");
            		    	   data.put(URLDecoder.decode(key_val[0]),URLDecoder.decode(key_val[1]));
            		    	}
            		       Verify(req,data);
            		    }
            		});
            	}
            	
            	else{
            		req.response.putHeader("content-type", "text/plain");
            		req.response.statusCode    = 405;
            		req.response.statusMessage = "Method not supported";
            		req.response.end();
            	}	
            }
        }).listen(8080);
    }
    
    public void Verify(HttpServerRequest req, Map <String,String> data){
    	String jsonrequest;
    	String result;
    	
    	if (!data.get("jsonrequest").equals(null)){
    	   if (req.method.equals("GET")){
    		   jsonrequest = Base64.decodeFast(data.get("jsonrequest")).toString();
           }
    	   else{
    		   jsonrequest = data.get("jsonrequest");
    	   }    		
    	   
    	   
    	}
    	
    	else{
    		
    	}
    
    }
}

