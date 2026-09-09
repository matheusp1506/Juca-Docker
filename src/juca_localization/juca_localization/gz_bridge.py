import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from ros_gz_interfaces.srv import SetEntityPose
from ros_gz_interfaces.msg import Entity

class GzPoseServiceBridge(Node):
    def __init__(self):
        super().__init__('gz_pose_bridge')

        # 1. Create client for Gazebo's SetEntityPose service
        self.client = self.create_client(SetEntityPose, '/world/empty/set_pose')
        
        self.get_logger().info("Waiting for /world/empty/set_pose service...")
        while not self.client.wait_for_service(timeout_sec=2.0):
            self.get_logger().info("Still waiting for /world/empty/set_pose...")

        self.get_logger().info("Connected to /world/empty/set_pose! Subscribing to /juca/odometry/filtered...")

        # 2. Subscribe to EKF filtered odometry
        self.sub = self.create_subscription(
            Odometry,
            '/juca/odometry/filtered',
            self.odom_callback,
            10
        )

        # Entity description for Juca model in Gazebo
        self.entity = Entity()
        self.entity.name = 'juca'
        self.entity.type = Entity.MODEL

        self.req_in_flight = False

    def odom_callback(self, msg: Odometry):
        # Throttle service calls: don't pile up requests if Gazebo is processing
        if self.req_in_flight or not self.client.service_is_ready():
            return

        req = SetEntityPose.Request()
        req.entity = self.entity
        req.pose = msg.pose.pose

        self.req_in_flight = True
        future = self.client.call_async(req)
        future.add_done_callback(self.response_callback)

    def response_callback(self, future):
        self.req_in_flight = False
        try:
            res = future.result()
            if not res.success:
                self.get_logger().warn("SetEntityPose returned failure", throttle_duration_sec=2.0)
        except Exception as e:
            self.get_logger().error(f"SetEntityPose service call failed: {e}")

def main(args=None):
    rclpy.init(args=args)
    node = GzPoseServiceBridge()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()