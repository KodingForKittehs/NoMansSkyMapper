import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

// Scene setup
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 2000);
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setClearColor(0x000000);
document.getElementById('container').appendChild(renderer.domElement);

// Controls
const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.05;

// Lighting
const ambientLight = new THREE.AmbientLight(0x404040);
scene.add(ambientLight);

const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
directionalLight.position.set(1, 1, 1);
scene.add(directionalLight);

// Load and parse CSV data
async function loadSystemData() {
    const response = await fetch('zamytaeus_anomaly.csv');
    const text = await response.text();
    const lines = text.split('\n').slice(1); // Skip header
    
    const points = [];
    const names = [];
    
    lines.forEach(line => {
        if (line.trim()) {
            const [name, x, y, z] = line.split(',');
            points.push(new THREE.Vector3(
                parseFloat(x),
                parseFloat(y),
                parseFloat(z)
            ));
            names.push(name);
        }
    });
    
    return { points, names };
}

// Create system spheres
function createSystems(points, names) {
    const geometry = new THREE.SphereGeometry(1, 16, 16);
    const material = new THREE.MeshPhongMaterial({
        color: 0xffff00,
        emissive: 0x002200,
        shininess: 100
    });
    
    points.forEach((point, index) => {
        const sphere = new THREE.Mesh(geometry, material);
        sphere.position.copy(point);
        sphere.userData.name = names[index];
        scene.add(sphere);
        
        // Add text label
        const canvas = document.createElement('canvas');
        const context = canvas.getContext('2d');
        canvas.width = 256;
        canvas.height = 64;
        context.fillStyle = 'white';
        context.font = '24px Arial';
        context.fillText(names[index], 10, 32);
        
        const texture = new THREE.CanvasTexture(canvas);
        const labelMaterial = new THREE.SpriteMaterial({ map: texture });
        const label = new THREE.Sprite(labelMaterial);
        label.position.copy(point);
        label.position.y += 2; // Raise label above sphere
        label.scale.set(20, 5, 1);
        scene.add(label);
    });
}

// Handle window resize
window.addEventListener('resize', () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
});

// Animation loop
function animate() {
    requestAnimationFrame(animate);
    controls.update();
    renderer.render(scene, camera);
}

// Initialize
async function init() {
    const { points, names } = await loadSystemData();
    
    // Center camera on data
    const center = new THREE.Vector3();
    points.forEach(point => center.add(point));
    center.divideScalar(points.length);
    
    // Find the furthest point to set camera distance
    let maxDistance = 0;
    points.forEach(point => {
        const distance = point.distanceTo(center);
        maxDistance = Math.max(maxDistance, distance);
    });
    
    camera.position.copy(center);
    camera.position.z += maxDistance * 2;
    camera.lookAt(center);
    
    createSystems(points, names);
    animate();
}

init(); 