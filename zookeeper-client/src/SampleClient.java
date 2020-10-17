// https://www.tutorialspoint.com/zookeeper/zookeeper_api.htm
// TODO: imports and stuff
import org.apache.zookeeper.ZooKeeper;
import org.apache.zookeeper.KeeperException;

public class SampleClient {
	private static ZooKeeper zoo;
	private static ZooKeeperConnection conn;

	public static void run() throws KeeperException, InterruptedException {
		//do stuff like creating zNodes and stuff
		String path = "/JustAnotherZnode";
		byte [] data = "I am written from Client code!".getBytes();
		ZnodeManager.create(path, data);

		if (ZnodeManager.exists(path)) {
			System.out.println("The Znode exists, yay!");
		} else {
			System.out.println("Oh oh, something is wrong...");
		}

	}

	public static void main(String[] args) {
		if (args.length != 1) {
			System.out.println("[ERROR] expected one argument");
			System.exit(1);
		}
		String host = args[0];
		try {
			conn = new ZooKeeperConnection();
			zoo = conn.connect(host);
			run();
			conn.close();
		} catch (Exception e) {
			System.out.println(e.getMessage());
		}
	}
}