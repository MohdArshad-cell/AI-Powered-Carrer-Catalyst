import React, { useRef } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Torus } from '@react-three/drei';

function Shape() {
  const meshRef = useRef();

  // This hook runs on every frame, creating the animation
  useFrame((state, delta) => {
    // Rotate the shape
    meshRef.current.rotation.x += delta * 0.2;
    meshRef.current.rotation.y += delta * 0.2;

    // Make it subtly follow the mouse
    const { pointer } = state;
    meshRef.current.position.x = pointer.x * 2;
    meshRef.current.position.y = pointer.y * 2;
  });

  return (
    <Torus ref={meshRef} args={[1.5, 0.4, 32, 100]}>
      <meshStandardMaterial 
        color="#00F6FF" 
        emissive="#6248FF" 
        metalness={0.9} 
        roughness={0.1} 
      />
    </Torus>
  );
}

export default function Scene() {
  return (
    <div className="hero-3d-canvas">
      <Canvas>
        <ambientLight intensity={0.5} />
        <pointLight position={[10, 10, 10]} intensity={1.5} />
        <Shape />
      </Canvas>
    </div>
  );
}