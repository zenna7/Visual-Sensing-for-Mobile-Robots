
#include <chrono>
#include <memory>

#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/string.hpp"

using namespace std::chrono_literals;

class FirstPublisher : public rclcpp::Node
{
public:
    FirstPublisher() : Node("first_publisher")
    {
        publisher_ = create_publisher<std_msgs::msg::String>(
            "/slam/status_demo", 10
        );

        timer_ = create_wall_timer(
            1s,
            [this]() {
                std_msgs::msg::String msg;
                msg.data = "WAITING_FOR_CAMERA";

                publisher_->publish(msg);
            }
        );
    }

private:
    rclcpp::Publisher<std_msgs::msg::String>::SharedPtr publisher_;
    rclcpp::TimerBase::SharedPtr timer_;
};

int main(int argc, char **argv)
{
    rclcpp::init(argc, argv);
    rclcpp::spin(std::make_shared<FirstPublisher>());
    rclcpp::shutdown();
    return 0;
}
