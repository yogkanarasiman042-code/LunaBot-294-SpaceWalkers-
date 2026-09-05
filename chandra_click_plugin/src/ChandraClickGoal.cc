#include <iostream>

#include <QEvent>
#include <QObject>

#include <gz/gui/Application.hh>
#include <gz/gui/GuiEvents.hh>
#include <gz/gui/Plugin.hh>
#include <gz/plugin/Register.hh>
#include <gz/transport/Node.hh>
#include <gz/msgs/vector3d.pb.h>

#include <gz/rendering/Camera.hh>
#include <gz/rendering/RayQuery.hh>
#include <gz/rendering/RenderingIface.hh>
#include <gz/rendering/Scene.hh>
#include <gz/rendering/Utils.hh>

#include <gz/math/Vector2.hh>

class ChandraClickGoal : public gz::gui::Plugin
{
public:
  ChandraClickGoal()
  {
  }

public:
  void LoadConfig(const tinyxml2::XMLElement *) override
  {
    std::cout
      << "[CHANDRA] Click-to-go plugin loaded."
      << std::endl;

    this->goalPublisher =
      this->transportNode.Advertise<gz::msgs::Vector3d>(
        "/chandra/clicked_goal"
      );

    gz::gui::App()->installEventFilter(this);
  }

protected:
  bool eventFilter(QObject *_obj, QEvent *_event) override
  {
    (void)_obj;

    if (_event->type() !=
        gz::gui::events::MousePressOnScene::kType)
    {
      return false;
    }

    auto *mouseEvent =
      static_cast<gz::gui::events::MousePressOnScene *>(_event);

    const auto &mouse = mouseEvent->Mouse();

    // Only react to left mouse button.
    if (mouse.Button() != gz::common::MouseEvent::LEFT)
      return false;

    auto scene = gz::rendering::sceneFromFirstRenderEngine();

    if (!scene)
    {
      std::cerr
        << "[CHANDRA] Rendering scene unavailable."
        << std::endl;
      return false;
    }

    gz::rendering::CameraPtr camera;

    for (unsigned int i = 0; i < scene->NodeCount(); ++i)
    {
      auto node = scene->NodeByIndex(i);

      if (!node)
        continue;

      auto candidate =
        std::dynamic_pointer_cast<gz::rendering::Camera>(node);

      if (candidate)
      {
        camera = candidate;
        break;
      }
    }

    if (!camera)
    {
      std::cerr
        << "[CHANDRA] User camera unavailable."
        << std::endl;
      return false;
    }

    auto rayQuery = scene->CreateRayQuery();

    gz::math::Vector2i screenPos(
      mouse.Pos().X(),
      mouse.Pos().Y()
    );

    auto world =
      gz::rendering::screenToPlane(
        screenPos,
        camera,
        rayQuery,
        0.0f
      );

    std::cout
      << "\n🌙 CHANDRA TARGET"
      << " | X=" << world.X()
      << " | Y=" << world.Y()
      << " | Z=" << world.Z()
      << std::endl;

    gz::msgs::Vector3d msg;
    msg.set_x(world.X());
    msg.set_y(world.Y());
    msg.set_z(world.Z());

    this->goalPublisher.Publish(msg);

    return false;
  }
private:
  gz::transport::Node transportNode;
  gz::transport::Node::Publisher goalPublisher;
};

GZ_ADD_PLUGIN(
  ChandraClickGoal,
  gz::gui::Plugin
)

