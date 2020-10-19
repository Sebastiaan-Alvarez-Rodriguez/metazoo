import org.apache.zookeeper.*;
import org.apache.zookeeper.server.PurgeTxnLog;

import java.io.File;
import java.io.IOException;
import java.nio.file.Paths;

public class ZnodeManager {
	private static ZooKeeper zoo;

	public ZnodeManager(ZooKeeper zk) { zoo = zk;}

	//creates a zNode (Synchronous)
	public void create(String path, byte[] data) throws KeeperException, InterruptedException {
		zoo.create(path, data, ZooDefs.Ids.OPEN_ACL_UNSAFE, CreateMode.PERSISTENT);
	}

	//checks if znode exists (Synchronous)
	public boolean exists(String path) throws InterruptedException, KeeperException {
		return zoo.exists(path, true) != null;
	}

	//deletes the znode (Synchronous)
	public void delete(String path) throws KeeperException, InterruptedException {
		zoo.delete(path, get_version(path));
	}


	//gets the Data of a znode (Asynchronous)
	public void getData_async(String path, AsyncCallback.DataCallback db) {
		zoo.getData(path, false, db, null);
	}


	//sets the Data of a znode (Asynchronous)
	public void setData_async(String path, byte[] data, AsyncCallback.StatCallback sb) throws KeeperException, InterruptedException {
		zoo.setData(path, data, get_version(path), sb, null);
	}

	//return the current version of the zNode
	private int get_version(String path) throws KeeperException, InterruptedException {
		return zoo.exists(path, true).getVersion();
	}

	//purges snapshots and logs except the last num
	public void purge(String dataDirPath, int num) throws IOException {
		File file = Paths.get(dataDirPath).toFile();
		PurgeTxnLog.purge(file, file, num);
	}
}