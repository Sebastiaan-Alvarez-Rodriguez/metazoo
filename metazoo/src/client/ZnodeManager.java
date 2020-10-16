import org.apache.zookeeper.ZooKeeper;
import org.apache.zookeeper.KeeperException;
import org.apache.zookeeper.CreateMode;
import org.apache.zookeeper.ZooDefs;

public class ZnodeManager {
	private static ZooKeeper zoo;

	public ZnodeManager(ZooKeeper zk) {
		zoo = zk;
	}

	//creates a zNode
	public static void create(String path, byte[] data) throws KeeperException, InterruptedException {
		zoo.create(path, data, ZooDefs.Ids.OPEN_ACL_UNSAFE, CreateMode.PERSISTENT);
	}

	//checks if znode exists
	public static boolean exists(String path) throws InterruptedException, KeeperException {
		return zoo.exists(path, true) != null;
	}
}