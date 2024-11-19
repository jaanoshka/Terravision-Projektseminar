import React, { useEffect, useState, useRef } from "react";
import { useLocation } from "react-router-dom";
import { Canvas, useFrame } from "@react-three/fiber";
import { OrbitControls } from "@react-three/drei";
import { PLYLoader } from "three/examples/jsm/loaders/PLYLoader";
import * as THREE from "three";

const RotatingMesh = ({ geometry }: { geometry: THREE.BufferGeometry }) => {
  const meshRef = useRef<THREE.Mesh>(null);

  useFrame(() => {
    if (meshRef.current) {
      meshRef.current.rotation.y += 0.0; // Slow rotation for better visualization
    }
  });

  return (
    <mesh ref={meshRef} geometry={geometry}>
      <meshStandardMaterial vertexColors={true} flatShading={true} />
    </mesh>
  );
};

const View3 = () => {
  const [geometry, setGeometry] = useState<THREE.BufferGeometry | null>(null);
  const [meshFile, setMeshFile] = useState<string | null>(null);
  const location = useLocation();
  const address = location.state.address;
  const model = location.state.model;
  const loader = new PLYLoader();
  const [volume, setVolume] = useState<number | null>(null);
  const [area, setArea] = useState<number | null>(null);

  useEffect(() => {
    fetch(`http://localhost:4000/image/volume/${address}/${model}`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
      },
    })
      .then((res) => res.json())
      .then((result) => {
        if (result.error) {
          console.error("Error fetching volume:", result.error);
        } else {
          setVolume(result.total_volume);
          setArea(result.total_area);
        }
      })
      .catch((error) => console.error("Error:", error));
  }, []);

  useEffect(() => {
    fetch(`http://localhost:4000/mesh/ply/${address}/${model}`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
      },
    })
      .then((res) => res.blob())
      .then((blob) => {
        const url = URL.createObjectURL(blob);
        setMeshFile(url);
        loader.load(
          url,
          (geometry) => {
            geometry.computeBoundingBox();
            const boundingBox = geometry.boundingBox;
            if (boundingBox) {
              const center = new THREE.Vector3();
              boundingBox.getCenter(center);
              geometry.translate(-center.x, -center.y, -center.z);
            }

            geometry.scale(0.3, 0.3, 0.3);
            geometry.computeVertexNormals();
            setGeometry(geometry);
          },
          undefined,
          (error) => console.error("Error loading mesh:", error)
        );
      });
  }, []);

  return (
    <div
      style={{
        display: "grid",
        gridTemplateColumns: "30% 70%",
        height: "100vh",
        overflow: "hidden",
      }}
    >
      {/* Sidebar */}
      <div
        style={{
          background: "rgba(255, 255, 255, 0.1)",
          padding: "20px",
          borderRadius: "15px",
          boxShadow: "0px 4px 15px rgba(0, 0, 0, 0.2)",
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          alignItems: "center",
        }}
      >
        <table style={{ width: "100%", textAlign: "left" }}>
          <tbody>
            <tr>
              <td style={{ textAlign: "left"}}>Address:</td>
              <td style={{ textAlign: "right" }}>{address}</td>
            </tr>
            <br></br>
            <tr>
              <td style={{ textAlign: "left" }}>Model:</td>
              <td style={{ textAlign: "right" }}>{model}</td>
            </tr>
            <br></br>
            {volume !== null && (
              <tr>
                <td style={{ textAlign: "left" }}>Volume:</td>
                <td style={{ textAlign: "right" }}>{volume.toFixed(2)} m³</td>
              </tr>
            )}<br></br>
            {area !== null && (
              <tr>
                <td style={{ textAlign: "left" }}>Area:</td>
                <td style={{ textAlign: "right" }}>{area.toFixed(2)} m²</td>
              </tr>
            )}<br></br>
          </tbody>
        </table>
      </div>

      {/* Mesh Display */}
      <div style={{ width: "100%", height: "100%", position: "relative" }}>
        {meshFile && (
          <a
          href={meshFile}
          download={`${address.replace(/ /g, "_")}_mesh.ply`}
          style={{
            position: "absolute",
            top: "30px",
            right: "30px",
            padding: "10px 20px",
            backgroundColor: "rgba(255, 255, 255, 0.8)",
            color: "#fff",
            textDecoration: "none",
            borderRadius: "5px",
            boxShadow: "0px 2px 5px rgba(0, 0, 0, 0.3)",
            bottom: "10px",
            width: "30px",
            height: "30px",
            display: "flex",
            alignItems: "center",
            justifyContent: "center"
          }}
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            style={{
              width: "15px",
              height: "15px",
              color: "#007bff",
            }}
          >
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
            <polyline points="7 10 12 15 17 10" />
            <line x1="12" y1="15" x2="12" y2="3" />
          </svg>
        </a>
        )}
        <Canvas
          camera={{
            position: [0, 100, 13],
            up: [0, 0, 1],
            fov: 50,
          }}
          style={{ width: "100%", height: "100%" }}
          shadows
        >
          <ambientLight intensity={2.5} />
          <directionalLight position={[10, 10, 10]} intensity={1} />
          {geometry && <RotatingMesh geometry={geometry} />}
          <OrbitControls
            enablePan={false}
            enableZoom={true}
            target={[0, 0, 0]}
            up={[0, 0, 1]}
          />
        </Canvas>
      </div>
    </div>
  );
};

export default View3;
