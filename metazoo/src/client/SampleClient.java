// https://www.tutorialspoint.com/zookeeper/zookeeper_api.htm
// TODO: imports and stuff
import java.io.IOException;

import ZooKeeperConnection;
import ZnodeManager;


public class SampleClient {
	private static ZooKeeper zoo; 
	private static ZooKeeperConnection conn; 
	private static ZnodeManager nodes; 

	public static void run() {
		//do stuff like creating zNodes and stuff

	}

	public static void main(String[] args) {
		//connect with host
		try {
			conn = new ZooKeeperConnection();
			//TODO: change by zookeeper server address 
			zoo = conn.connect("localhost");
			nodes = new ZnodeManager(zoo);
			//TODO: parameters and stuff
			run();
			conn.close();
		} catch (Exception e) {
			System.out.println(e.getMessage());
		}
		//run
	}
}