import { useEffect, useState, useMemo } from "react";
import Particles, { initParticlesEngine } from "@tsparticles/react";
import { loadFull } from "tsparticles";

const ParticleBackground = () => {
  const [init, setInit] = useState(false);

  // This will run only once, when the component first mounts.
  useEffect(() => {
    initParticlesEngine(async (engine) => {
      // This loads the full bundle of features for the particles
      await loadFull(engine);
    }).then(() => {
      // Once the engine is ready, we set the init state to true
      setInit(true);
    });
  }, []);

  // We use useMemo to prevent the options object from being recreated on every render
  const particlesConfig = useMemo(
    () => ({
      background: {
        color: {
          value: "transparent",
        },
      },
      fpsLimit: 60,
      interactivity: {
        events: {
          onHover: {
            enable: false,
            mode: "repulse",
          },
          resize: true,
        },
        modes: {
          repulse: {
            distance: 100,
            duration: 0.4,
          },
        },
      },
      particles: {
        color: {
          value: "#ffffff",
        },
        links: {
          color: "#ffffff",
          distance: 150,
          enable: true,
          opacity: 0.1,
          width: 1,
        },
        collisions: {
          enable: true,
        },
        move: {
          direction: "none",
          enable: true,
          outModes: {
            default: "bounce",
          },
          random: false,
          speed: 1,
          straight: false,
        },
        number: {
          density: {
            enable: true,
            area: 800,
          },
          value: 50,
        },
        opacity: {
          value: 0.1,
        },
        shape: {
          type: "circle",
        },
        size: {
          value: { min: 1, max: 3 },
        },
      },
      detectRetina: true,
    }),
    [],
  );

  // Only render the Particles component after the engine is initialized
  if (init) {
    return (
      <Particles
        id="tsparticles"
        options={particlesConfig}
        style={{
          position: 'fixed',
          top: 0,
          left: 0,
          width: '100%',
          height: '100%',
          zIndex: -1
        }}
      />
    );
  }

  // While the engine is loading, we render nothing
  return <></>;
};

export default ParticleBackground;