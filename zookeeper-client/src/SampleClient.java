// https://www.tutorialspoint.com/zookeeper/zookeeper_api.htm
import org.apache.zookeeper.ZooKeeper;
import org.apache.zookeeper.KeeperException;
import org.apache.log4j.Logger;

public class SampleClient {
	private static ZooKeeper zoo;
	private static ZooKeeperConnection conn;
	private static ZnodeManager nodes;
	private static Logger LOG;

	public static void run() throws KeeperException, InterruptedException {
		String path = "/JustAnotherZnode";
		byte [] data = "I am written from Client code!".getBytes();
		if (!nodes.exists(path))
			nodes.create(path, data);

		if (nodes.exists(path)) {
			System.out.println("[CLIENT] The Znode exists, yay!");
			LOG.info("The client has created a Znode");
		} else {
			System.out.println("[CLIENT] Oh oh, something is wrong...");
			LOG.error("Something went wrong with the client");
		}
	}

	public static void main(String[] args) {
		LOG = Logger.getLogger(SampleClient.class);
		if (args.length != 1) {
			System.out.println("[ERROR] expected one argument");
			System.exit(1);
		}
		String host = args[0];
		try {
			LOG.info("This is some info message, from the client");
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