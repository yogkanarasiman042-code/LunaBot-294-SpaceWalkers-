#!/usr/bin/env python3

import rclpy

from rclpy.node import Node
from rclpy.action import ActionClient

from geometry_msgs.msg import Vector3
from nav2_msgs.action import NavigateToPose


class ChandraClickToNav(Node):

    def __init__(self):
        super().__init__('chandra_click_to_nav')

        self.nav_client = ActionClient(
            self,
            NavigateToPose,
            '/navigate_to_pose'
        )

        self.create_subscription(
            Vector3,
            '/chandra/clicked_goal',
            self.clicked_goal_callback,
            10
        )

        self.get_logger().info(
            '🌙 CHANDRA CLICK-TO-GO READY'
        )

        self.get_logger().info(
            'Click any reachable lunar ground point in Gazebo.'
        )

    def clicked_goal_callback(self, msg):

        x = float(msg.x)
        y = float(msg.y)

        self.get_logger().info(
            f'🎯 Gazebo target received: X={x:.2f}, Y={y:.2f}'
        )

        if not self.nav_client.wait_for_server(timeout_sec=2.0):
            self.get_logger().error(
                'Nav2 NavigateToPose server unavailable'
            )
            return

        goal = NavigateToPose.Goal()

        goal.pose.header.frame_id = 'map'
        goal.pose.header.stamp = self.get_clock().now().to_msg()

        goal.pose.pose.position.x = x
        goal.pose.pose.position.y = y
        goal.pose.pose.position.z = 0.0

        goal.pose.pose.orientation.x = 0.0
        goal.pose.pose.orientation.y = 0.0
        goal.pose.pose.orientation.z = 0.0
        goal.pose.pose.orientation.w = 1.0

        future = self.nav_client.send_goal_async(goal)
        future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):

        goal_handle = future.result()

        if not goal_handle.accepted:
            self.get_logger().warning(
                '❌ Chandra navigation goal rejected'
            )
            return

        self.get_logger().info(
            '✅ Goal accepted — Chandra navigating'
        )

        result_future = goal_handle.get_result_async()
        result_future.add_done_callback(
            self.result_callback
        )

    def result_callback(self, future):

        status = future.result().status

        if status == 4:
            self.get_logger().info(
                '🌙 ✅ CHANDRA REACHED CLICKED LOCATION'
            )
        else:
            self.get_logger().warning(
                f'Navigation ended with status {status}'
            )


def main():

    rclpy.init()

    node = ChandraClickToNav()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    node.destroy_node()

    if rclpy.ok():
        rclpy.shutdown()


if __name__ == '__main__':
    main()
