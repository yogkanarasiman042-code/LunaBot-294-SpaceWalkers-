import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient

from nav2_msgs.action import NavigateToPose
from geometry_msgs.msg import PoseStamped
from std_msgs.msg import String


class LunaBotPatrol(Node):

    def __init__(self):
        super().__init__('lunabot_patrol')

        # ============================================================
        # NAV2 ACTION CLIENT
        # ============================================================

        self.client = ActionClient(
            self,
            NavigateToPose,
            'navigate_to_pose'
        )

        # ============================================================
        # FINAL LUNAR HABITAT PATROL ROUTE
        # ============================================================

        # Approach points for the four operational stations.
        # These are intentionally placed near the stations rather
        # than inside their collision geometry.
        self.patrol_stations = [
            ('Habitat Module', 9.0, -9.0),
            ('Oxygen Station', 9.0, 9.0),
            ('Research Zone', -9.0, 9.0),
            ('Airlock', -9.0, -9.0),
        ]

        # Same named zones used by Mission Manager.
        self.zone_coordinates = {
            'Habitat Module': (9.0, -9.0),
            'Oxygen Station': (9.0, 9.0),
            'Research Zone': (-9.0, 9.0),
            'Airlock': (-9.0, -9.0),
        }

        self.current_waypoint = 0

        self.current_priority = None
        self.pending_priority = None

        self.goal_active = False

        self.active_mission_type = None
        self.active_zone = None

        # Prevent endless retry loops if Nav2 aborts.
        self.navigation_failed = False

        # ============================================================
        # MISSION MANAGER SUBSCRIPTION
        # ============================================================

        self.priority_sub = self.create_subscription(
            String,
            '/lunabot/priority_zone',
            self.priority_callback,
            10
        )

        self.get_logger().info(
            '🌙 LunaBot Adaptive Lunar Patrol Started'
        )

        self.get_logger().info(
            'Waiting for Nav2...'
        )

        self.client.wait_for_server()

        self.get_logger().info(
            '✅ Nav2 connected'
        )

        self.send_next_patrol_goal()

    # ============================================================
    # PRIORITY UPDATE FROM MISSION MANAGER
    # ============================================================

    def priority_callback(self, msg):

        zone = msg.data

        # Normal habitat state
        if zone == 'NONE':
            return

        if zone not in self.zone_coordinates:

            self.get_logger().warning(
                f'Unknown priority zone: {zone}'
            )

            return

        # Ignore repeated priority messages
        if zone == self.current_priority:
            return

        self.current_priority = zone
        self.pending_priority = zone

        self.get_logger().warning(
            f'🚨 Mission priority updated: {zone}'
        )

        # Safe diversion:
        # if currently navigating, finish current goal first.
        # if idle, immediately dispatch priority mission.
        if not self.goal_active:
            self.send_priority_goal()

    # ============================================================
    # NORMAL STATION PATROL
    # ============================================================

    def send_next_patrol_goal(self):

        if self.goal_active:
            return

        if self.pending_priority is not None:
            self.send_priority_goal()
            return

        if self.navigation_failed:
            self.get_logger().warning(
                'Patrol paused after navigation failure'
            )
            return

        zone, x, y = self.patrol_stations[
            self.current_waypoint
        ]

        self.get_logger().info(
            f'🚀 Patrol Station '
            f'{self.current_waypoint + 1}/'
            f'{len(self.patrol_stations)}: '
            f'{zone} -> ({x:.1f}, {y:.1f})'
        )

        self.send_goal(
            x,
            y,
            mission_type='PATROL',
            zone=zone
        )

    # ============================================================
    # PRIORITY MISSION
    # ============================================================

    def send_priority_goal(self):

        if self.goal_active:
            return

        if self.pending_priority is None:
            return

        zone = self.pending_priority
        self.pending_priority = None

        x, y = self.zone_coordinates[zone]

        self.get_logger().warning(
            f'🎯 DIVERTING TO PRIORITY ZONE: '
            f'{zone} -> ({x:.1f}, {y:.1f})'
        )

        self.navigation_failed = False

        self.send_goal(
            x,
            y,
            mission_type='PRIORITY',
            zone=zone
        )

    # ============================================================
    # SEND NAV2 GOAL
    # ============================================================

    def send_goal(
        self,
        x,
        y,
        mission_type='PATROL',
        zone=None
    ):

        goal = NavigateToPose.Goal()

        goal.pose = PoseStamped()

        goal.pose.header.frame_id = 'map'

        goal.pose.header.stamp = (
            self.get_clock().now().to_msg()
        )

        goal.pose.pose.position.x = float(x)
        goal.pose.pose.position.y = float(y)
        goal.pose.pose.position.z = 0.0

        # Neutral final orientation
        goal.pose.pose.orientation.w = 1.0

        self.goal_active = True

        self.active_mission_type = mission_type
        self.active_zone = zone

        future = self.client.send_goal_async(goal)

        future.add_done_callback(
            self.goal_response_callback
        )

    # ============================================================
    # NAV2 GOAL RESPONSE
    # ============================================================

    def goal_response_callback(self, future):

        goal_handle = future.result()

        if not goal_handle.accepted:

            self.goal_active = False
            self.navigation_failed = True

            self.get_logger().warning(
                '❌ Navigation goal rejected'
            )

            return

        self.get_logger().info(
            '✅ Navigation goal accepted'
        )

        result_future = goal_handle.get_result_async()

        result_future.add_done_callback(
            self.result_callback
        )

    # ============================================================
    # NAVIGATION RESULT
    # ============================================================

    def result_callback(self, future):

        status = future.result().status

        self.goal_active = False

        # ROS action status 4 = SUCCEEDED
        if status == 4:

            self.navigation_failed = False

            if self.active_mission_type == 'PRIORITY':

                self.get_logger().info(
                    f'🚨 Priority zone reached: '
                    f'{self.active_zone}'
                )

                # Resume routine patrol afterward
                self.current_priority = None

            else:

                self.get_logger().info(
                    f'✅ Patrol station reached: '
                    f'{self.active_zone}'
                )

                self.current_waypoint += 1

                if self.current_waypoint >= len(
                    self.patrol_stations
                ):
                    self.current_waypoint = 0

        else:

            # IMPORTANT:
            # Do not immediately resend the failed goal.
            self.navigation_failed = True

            self.get_logger().warning(
                f'❌ Navigation ended with '
                f'status {status}'
            )

            self.get_logger().warning(
                'Automatic retry disabled to '
                'prevent goal-spam'
            )

            return

        # If an anomaly appeared while navigating,
        # it gets priority now.
        if self.pending_priority is not None:
            self.send_priority_goal()

        else:
            self.send_next_patrol_goal()


def main(args=None):

    rclpy.init(args=args)

    node = LunaBotPatrol()

    try:
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    node.destroy_node()

    if rclpy.ok():
        rclpy.shutdown()


if __name__ == '__main__':
    main()
