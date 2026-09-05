import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Float32


class LunaBotMissionManager(Node):

    def __init__(self):
        super().__init__('lunabot_mission_manager')

        # =========================================================
        # HABITAT ZONES
        # =========================================================

        # Base risk / inspection priority of each habitat zone
        self.zones = {
            'Habitat Module': 10,
            'Oxygen Station': 20,
            'Research Zone': 10,
            'Airlock': 15
        }

        # Temporary coordinates using our already-tested patrol area.
        # These will be updated after the final lunar habitat is built.
        self.zone_coordinates = {
    'Habitat Module': (9.0, -9.0),
    'Oxygen Station': (9.0, 9.0),
    'Research Zone': (-9.0, 9.0),
    'Airlock': (-9.0, -9.0)
}

        # =========================================================
        # DEFAULT ENVIRONMENT VALUES
        # =========================================================

        self.temperature = 22.0
        self.oxygen = 20.9

        # =========================================================
        # SUBSCRIBERS
        # =========================================================

        self.temp_sub = self.create_subscription(
            Float32,
            '/lunabot/temperature',
            self.temperature_callback,
            10
        )

        self.oxygen_sub = self.create_subscription(
            Float32,
            '/lunabot/oxygen',
            self.oxygen_callback,
            10
        )

        # =========================================================
        # PUBLISHERS
        # =========================================================

        # Complete mission state for dashboard / other nodes
        self.mission_pub = self.create_publisher(
            String,
            '/lunabot/mission_status',
            10
        )

        # Highest-priority habitat zone
        self.priority_pub = self.create_publisher(
            String,
            '/lunabot/priority_zone',
            10
        )

        # =========================================================
        # MISSION EVALUATION TIMER
        # =========================================================

        self.timer = self.create_timer(
            2.0,
            self.evaluate_mission
        )

        self.get_logger().info(
            '🌙 LunaBot Mission Manager Started'
        )

    # =============================================================
    # SENSOR CALLBACKS
    # =============================================================

    def temperature_callback(self, msg):
        self.temperature = msg.data

    def oxygen_callback(self, msg):
        self.oxygen = msg.data

    # =============================================================
    # RISK-AWARE MISSION LOGIC
    # =============================================================

    def evaluate_mission(self):

        # Start each evaluation using normal base priorities
        risks = self.zones.copy()

        # ---------------------------------------------------------
        # Oxygen anomaly
        # ---------------------------------------------------------

        if self.oxygen < 19.5:
            risks['Oxygen Station'] += 80

        # ---------------------------------------------------------
        # High-temperature anomaly
        # ---------------------------------------------------------

        if self.temperature > 35.0:
            risks['Habitat Module'] += 60

        # ---------------------------------------------------------
        # Low-temperature anomaly
        # ---------------------------------------------------------

        if self.temperature < 5.0:
            risks['Habitat Module'] += 50

        # ---------------------------------------------------------
        # Select highest-risk zone
        # ---------------------------------------------------------

        priority_zone = max(risks, key=risks.get)
        priority_score = risks[priority_zone]

        # Get navigation coordinates for selected zone
        target_x, target_y = self.zone_coordinates[priority_zone]

        # =========================================================
        # PUBLISH PRIORITY ZONE
        # =========================================================

        priority_msg = String()

        if priority_score >= 50:
            priority_msg.data = priority_zone
        else:
            priority_msg.data = 'NONE'

        self.priority_pub.publish(priority_msg)


        # =========================================================
        # PUBLISH COMPLETE MISSION STATUS
        # =========================================================

        status_msg = String()

        status_msg.data = (
            f'PRIORITY={priority_zone};'
            f'RISK={priority_score};'
            f'TARGET_X={target_x:.2f};'
            f'TARGET_Y={target_y:.2f};'
            f'TEMP={self.temperature:.1f};'
            f'O2={self.oxygen:.1f}'
        )

        self.mission_pub.publish(status_msg)

        # =========================================================
        # TERMINAL STATUS
        # =========================================================

        self.get_logger().info(
            f'🎯 Priority Zone: {priority_zone} | '
            f'Risk: {priority_score} | '
            f'Target: ({target_x:.2f}, {target_y:.2f}) | '
            f'Temp: {self.temperature:.1f}°C | '
            f'O2: {self.oxygen:.1f}%'
        )


def main(args=None):

    rclpy.init(args=args)

    node = LunaBotMissionManager()

    try:
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
