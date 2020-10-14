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
		String path = "/JustAnotherZnode";
		byte [] data = "I am written from Client code!".getBytes();
		nodes.create(path, data); 

		if (nodes.exists(path)) {
			System.out.println("The Znode exists, yay!");
		} else {
			System.out.println("Oh oh, something is wrong...");
		}

	}

	public static void main(String[] args) {
		if (args.length != 1) {
			System.out.println("[ERROR] expected one argument");
			exit(1);
		}
		String host = args[0];
		try {
			conn = new ZooKeeperConnection();
			zoo = conn.connect(host);
			nodes = new ZnodeManager(zoo);
			run();
			conn.close();
		} catch (Exception e) {
			System.out.println(e.getMessage());
		}
	}
}