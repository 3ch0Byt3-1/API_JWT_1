from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import aiohttp
import asyncio
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import binascii
import time
import uuid
from datetime import datetime
import json
import os

# Try to import protobuf modules with better error handling
try:
    import MajorLoginReq_pb2
    import MajorLoginRes_pb2
    import jwt_generator_pb2
    PROTOBUF_AVAILABLE = True
    print("✅ Protobuf modules loaded successfully")
except ImportError as e:
    print(f"❌ Protobuf import error: {e}")
    PROTOBUF_AVAILABLE = False

# Constants
AES_KEY = b'Yg&tc%DEuh6%Zc^8'
AES_IV = b'6oyZDr22E3ychjM%'

# Flask App
app = Flask(__name__)
CORS(app)

# Global statistics
stats = {
    'total_requests': 0,
    'successful_logins': 0,
    'failed_logins': 0,
    'avg_response_time': 0
}

class Service:
    def __init__(self):
        self.session = None
        
    async def get_session(self):
        if not self.session:
            timeout = aiohttp.ClientTimeout(total=10)
            connector = aiohttp.TCPConnector(limit=100, verify_ssl=False)
            self.session = aiohttp.ClientSession(timeout=timeout, connector=connector)
        return self.session
    
    async def close_session(self):
        if self.session:
            await self.session.close()
            
    def encrypt_message(self, plaintext):
        try:
            cipher = AES.new(AES_KEY, AES.MODE_CBC, AES_IV)
            padded = pad(plaintext, AES.block_size)
            return cipher.encrypt(padded)
        except Exception as e:
            raise Exception(f"Encryption error: {e}")
    
    def decrypt_message(self, ciphertext):
        try:
            cipher = AES.new(AES_KEY, AES.MODE_CBC, AES_IV)
            decrypted = cipher.decrypt(ciphertext)
            return unpad(decrypted, AES.block_size)
        except Exception as e:
            raise Exception(f"Decryption error: {e}")

# Initialize service
_service = Service()

# HTML UI Template (same as yours)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🚀 Free Fire Token Generator</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {
            --primary: #6366f1;
            --secondary: #8b5cf6;
            --accent: #06b6d4;
            --dark: #0f172a;
            --darker: #020617;
            --light: #f1f5f9;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            background: linear-gradient(135deg, var(--darker) 0%, var(--dark) 50%, #1e293b 100%);
            min-height: 100vh;
            font-family: 'Inter', sans-serif;
            overflow-x: hidden;
        }
        
        .glass-morphism {
            background: rgba(15, 23, 42, 0.7);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        }
        
        .neon-glow {
            box-shadow: 
                0 0 5px var(--primary),
                0 0 10px var(--primary),
                0 0 15px var(--primary),
                0 0 20px var(--secondary);
        }
        
        .gradient-text {
            background: linear-gradient(135deg, var(--accent) 0%, var(--primary) 50%, var(--secondary) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .pulse-animation {
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0% { transform: scale(1); box-shadow: 0 0 0 0 rgba(99, 102, 241, 0.7); }
            70% { transform: scale(1.05); box-shadow: 0 0 0 10px rgba(99, 102, 241, 0); }
            100% { transform: scale(1); box-shadow: 0 0 0 0 rgba(99, 102, 241, 0); }
        }
        
        .float-animation {
            animation: float 6s ease-in-out infinite;
        }
        
        @keyframes float {
            0% { transform: translateY(0px); }
            50% { transform: translateY(-20px); }
            100% { transform: translateY(0px); }
        }
        
        .glow-border {
            position: relative;
            border: 2px solid transparent;
            background: linear-gradient(var(--dark), var(--dark)) padding-box,
                        linear-gradient(135deg, var(--primary), var(--secondary)) border-box;
        }
        
        .particle {
            position: absolute;
            background: rgba(99, 102, 241, 0.3);
            border-radius: 50%;
            pointer-events: none;
        }
        
        .typing-animation {
            overflow: hidden;
            border-right: 2px solid var(--accent);
            white-space: nowrap;
            animation: typing 3.5s steps(40, end), blink-caret 0.75s step-end infinite;
        }
        
        @keyframes typing {
            from { width: 0 }
            to { width: 100% }
        }
        
        @keyframes blink-caret {
            from, to { border-color: transparent }
            50% { border-color: var(--accent) }
        }
        
        .flip-card {
            perspective: 1000px;
        }
        
        .flip-card-inner {
            transition: transform 0.6s;
            transform-style: preserve-3d;
        }
        
        .flip-card:hover .flip-card-inner {
            transform: rotateY(180deg);
        }
        
        .flip-card-front, .flip-card-back {
            backface-visibility: hidden;
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
        }
        
        .flip-card-back {
            transform: rotateY(180deg);
        }
        
        .stagger-animation > * {
            opacity: 0;
            transform: translateY(20px);
            animation: stagger 0.5s ease forwards;
        }
        
        @keyframes stagger {
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .stagger-animation > *:nth-child(1) { animation-delay: 0.1s; }
        .stagger-animation > *:nth-child(2) { animation-delay: 0.2s; }
        .stagger-animation > *:nth-child(3) { animation-delay: 0.3s; }
        .stagger-animation > *:nth-child(4) { animation-delay: 0.4s; }
        .stagger-animation > *:nth-child(5) { animation-delay: 0.5s; }
    </style>
</head>
<body class="text-gray-300">
    <!-- Animated Background Particles -->
    <div id="particles-container" class="fixed inset-0 pointer-events-none z-0"></div>
    
    <!-- Navigation -->
    <nav class="glass-morphism sticky top-0 z-50">
        <div class="container mx-auto px-4 py-4">
            <div class="flex justify-between items-center">
                <div class="flex items-center space-x-2">
                    <i class="fas fa-rocket text-2xl text-indigo-400"></i>
                    <span class="text-xl font-bold gradient-text">Token</span>
                </div>
                
                <div class="hidden md:flex space-x-6">
                    <a href="#home" class="hover:text-indigo-400 transition-colors">Home</a>
                    <a href="#features" class="hover:text-indigo-400 transition-colors">Features</a>
                    <a href="#generator" class="hover:text-indigo-400 transition-colors">Generator</a>
                    <a href="#stats" class="hover:text-indigo-400 transition-colors">Statistics</a>
                </div>
                
                <div class="flex items-center space-x-4">
                    <div class="hidden md:flex items-center space-x-2 text-sm">
                        <div class="w-2 h-2 bg-green-500 rounded-full pulse-animation"></div>
                        <span>API Online</span>
                    </div>
                    <button class="bg-gradient-to-r from-indigo-500 to-purple-600 px-4 py-2 rounded-lg font-medium hover:from-indigo-600 hover:to-purple-700 transition-all">
                        <i class="fas fa-crown mr-2"></i>
                    </button>
                </div>
            </div>
        </div>
    </nav>

    <!-- Hero Section -->
    <section id="home" class="relative py-20 overflow-hidden">
        <div class="container mx-auto px-4">
            <div class="flex flex-col lg:flex-row items-center">
                <div class="lg:w-1/2 mb-12 lg:mb-0 stagger-animation">
                    <h1 class="text-5xl lg:text-6xl font-bold text-white mb-6 leading-tight">
                        <span class="gradient-text"> Free Fire</span><br>
                        Token Generator
                    </h1>
                    <p class="text-xl text-gray-400 mb-8 max-w-lg">
                        Generate  Free Fire tokens instantly with our advanced API. 
                        Fast, secure, and reliable token generation service.
                    </p>
                    <div class="flex flex-wrap gap-4">
                        <a href="#generator" class="bg-gradient-to-r from-indigo-500 to-purple-600 px-6 py-4 rounded-xl font-bold text-lg hover:from-indigo-600 hover:to-purple-700 transition-all glow-border pulse-animation">
                            <i class="fas fa-bolt mr-2"></i>Generate Token
                        </a>
                        <a href="#features" class="glass-morphism px-6 py-4 rounded-xl font-bold text-lg border border-gray-700 hover:border-indigo-500 transition-all">
                            <i class="fas fa-star mr-2"></i>Learn More
                        </a>
                    </div>
                    
                    <div class="mt-12 grid grid-cols-2 md:grid-cols-4 gap-6">
                        <div class="text-center">
                            <div class="text-3xl font-bold text-white">99.9%</div>
                            <div class="text-gray-400 text-sm">Uptime</div>
                        </div>
                        <div class="text-center">
                            <div class="text-3xl font-bold text-white">500ms</div>
                            <div class="text-gray-400 text-sm">Avg Response</div>
                        </div>
                        <div class="text-center">
                            <div class="text-3xl font-bold text-white">24/7</div>
                            <div class="text-gray-400 text-sm">Support</div>
                        </div>
                        <div class="text-center">
                            <div class="text-3xl font-bold text-white">SSL</div>
                            <div class="text-gray-400 text-sm">Secure</div>
                        </div>
                    </div>
                </div>
                
                <div class="lg:w-1/2 flex justify-center">
                    <div class="relative">
                        <div class="glass-morphism rounded-2xl p-8 max-w-md float-animation">
                            <div class="flex justify-between items-center mb-6">
                                <h3 class="text-xl font-bold text-white">Token Preview</h3>
                                <div class="flex space-x-2">
                                    <div class="w-3 h-3 bg-red-500 rounded-full"></div>
                                    <div class="w-3 h-3 bg-yellow-500 rounded-full"></div>
                                    <div class="w-3 h-3 bg-green-500 rounded-full"></div>
                                </div>
                            </div>
                            
                            <div class="space-y-4">
                                <div class="bg-gray-800 rounded-lg p-4">
                                    <div class="text-gray-400 text-sm">Account ID</div>
                                    <div class="text-white font-mono">294857362019</div>
                                </div>
                                <div class="bg-gray-800 rounded-lg p-4">
                                    <div class="text-gray-400 text-sm">Token Status</div>
                                    <div class="text-green-400 font-mono">Active</div>
                                </div>
                                <div class="bg-gray-800 rounded-lg p-4">
                                    <div class="text-gray-400 text-sm">Expires</div>
                                    <div class="text-white font-mono">24 hours</div>
                                </div>
                                <div class="bg-indigo-900 rounded-lg p-4 border border-indigo-700">
                                    <div class="text-indigo-300 text-sm"> Token</div>
                                    <div class="text-white font-mono truncate">eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...</div>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Floating elements -->
                        <div class="absolute -top-4 -right-4 w-8 h-8 bg-indigo-500 rounded-full opacity-70 float-animation" style="animation-delay: 1s;"></div>
                        <div class="absolute -bottom-4 -left-4 w-6 h-6 bg-purple-500 rounded-full opacity-70 float-animation" style="animation-delay: 2s;"></div>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- Features Section -->
    <section id="features" class="py-20">
        <div class="container mx-auto px-4">
            <div class="text-center mb-16">
                <h2 class="text-4xl font-bold text-white mb-4"> Features</h2>
                <p class="text-xl text-gray-400 max-w-2xl mx-auto">
                    Our advanced token generation service offers everything you need for seamless Free Fire gaming.
                </p>
            </div>
            
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                <!-- Feature 1 -->
                <div class="glass-morphism rounded-2xl p-6 hover:transform hover:-translate-y-2 transition-all duration-300 stagger-animation">
                    <div class="w-12 h-12 bg-indigo-500 rounded-xl flex items-center justify-center mb-4">
                        <i class="fas fa-bolt text-white text-xl"></i>
                    </div>
                    <h3 class="text-xl font-bold text-white mb-2">Lightning Fast</h3>
                    <p class="text-gray-400">
                        Generate tokens in under 500ms with our optimized API infrastructure and global CDN.
                    </p>
                </div>
                
                <!-- Feature 2 -->
                <div class="glass-morphism rounded-2xl p-6 hover:transform hover:-translate-y-2 transition-all duration-300 stagger-animation">
                    <div class="w-12 h-12 bg-purple-500 rounded-xl flex items-center justify-center mb-4">
                        <i class="fas fa-shield-alt text-white text-xl"></i>
                    </div>
                    <h3 class="text-xl font-bold text-white mb-2">Military Grade Security</h3>
                    <p class="text-gray-400">
                        AES-256 encryption and secure protocols ensure your data is always protected.
                    </p>
                </div>
                
                <!-- Feature 3 -->
                <div class="glass-morphism rounded-2xl p-6 hover:transform hover:-translate-y-2 transition-all duration-300 stagger-animation">
                    <div class="w-12 h-12 bg-cyan-500 rounded-xl flex items-center justify-center mb-4">
                        <i class="fas fa-infinity text-white text-xl"></i>
                    </div>
                    <h3 class="text-xl font-bold text-white mb-2">99.9% Uptime</h3>
                    <p class="text-gray-400">
                        Our redundant server infrastructure guarantees maximum availability and reliability.
                    </p>
                </div>
                
                <!-- Feature 4 -->
                <div class="glass-morphism rounded-2xl p-6 hover:transform hover:-translate-y-2 transition-all duration-300 stagger-animation">
                    <div class="w-12 h-12 bg-green-500 rounded-xl flex items-center justify-center mb-4">
                        <i class="fas fa-mobile-alt text-white text-xl"></i>
                    </div>
                    <h3 class="text-xl font-bold text-white mb-2">Mobile Optimized</h3>
                    <p class="text-gray-400">
                        Fully responsive design that works perfectly on all devices and screen sizes.
                    </p>
                </div>
                
                <!-- Feature 5 -->
                <div class="glass-morphism rounded-2xl p-6 hover:transform hover:-translate-y-2 transition-all duration-300 stagger-animation">
                    <div class="w-12 h-12 bg-yellow-500 rounded-xl flex items-center justify-center mb-4">
                        <i class="fas fa-crown text-white text-xl"></i>
                    </div>
                    <h3 class="text-xl font-bold text-white mb-2"> Tokens</h3>
                    <p class="text-gray-400">
                        Access exclusive  tokens with extended validity and enhanced features.
                    </p>
                </div>
                
                <!-- Feature 6 -->
                <div class="glass-morphism rounded-2xl p-6 hover:transform hover:-translate-y-2 transition-all duration-300 stagger-animation">
                    <div class="w-12 h-12 bg-red-500 rounded-xl flex items-center justify-center mb-4">
                        <i class="fas fa-headset text-white text-xl"></i>
                    </div>
                    <h3 class="text-xl font-bold text-white mb-2">24/7 Support</h3>
                    <p class="text-gray-400">
                        Our dedicated support team is available around the clock to assist you.
                    </p>
                </div>
            </div>
        </div>
    </section>

    <!-- Token Generator Section -->
    <section id="generator" class="py-20">
        <div class="container mx-auto px-4">
            <div class="max-w-4xl mx-auto">
                <div class="text-center mb-12">
                    <h2 class="text-4xl font-bold text-white mb-4">Token Generator</h2>
                    <p class="text-xl text-gray-400">
                        Enter your Free Fire credentials to generate a  token instantly.
                    </p>
                </div>
                
                <div class="glass-morphism rounded-2xl p-8 glow-border">
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
                        <div>
                            <label class="text-white text-sm font-medium mb-2 block">Free Fire UID</label>
                            <div class="relative">
                                <input type="text" id="uid" placeholder="Enter your UID" 
                                       class="w-full px-4 py-3 rounded-xl bg-gray-800 border border-gray-700 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all">
                                <div class="absolute right-3 top-3">
                                    <i class="fas fa-user text-gray-500"></i>
                                </div>
                            </div>
                        </div>
                        
                        <div>
                            <label class="text-white text-sm font-medium mb-2 block">Password</label>
                            <div class="relative">
                                <input type="password" id="password" placeholder="Enter your password" 
                                       class="w-full px-4 py-3 rounded-xl bg-gray-800 border border-gray-700 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all">
                                <div class="absolute right-3 top-3">
                                    <i class="fas fa-lock text-gray-500"></i>
                                </div>
                            </div>
                        </div>
                    </div>

                    <button onclick="generateToken()" 
                            class="w-full bg-gradient-to-r from-indigo-500 to-purple-600 text-white py-4 rounded-xl font-bold text-lg hover:from-indigo-600 hover:to-purple-700 transition-all duration-300 glow-border pulse-animation mb-6">
                        <i class="fas fa-bolt mr-2"></i>GENERATE  TOKEN
                    </button>
                    
                    <div class="text-center text-gray-400 text-sm">
                        <i class="fas fa-shield-alt mr-2"></i>Your credentials are encrypted and never stored
                    </div>
                </div>

                <!-- Result Display -->
                <div id="result" class="glass-morphism rounded-2xl p-8 mt-8 glow-border hidden">
                    <h3 class="text-2xl font-bold text-white mb-6 text-center">
                        <i class="fas fa-ticket-alt mr-2"></i>Token Generated Successfully
                    </h3>
                    
                    <div class="bg-gray-800 rounded-xl p-6 mb-6">
                        <pre id="resultData" class="text-white/90 font-mono text-sm overflow-x-auto"></pre>
                    </div>
                    
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <button onclick="copyToClipboard()" 
                                class="bg-green-600 text-white py-3 rounded-xl font-bold hover:bg-green-700 transition flex items-center justify-center">
                            <i class="fas fa-copy mr-2"></i>Copy Token
                        </button>
                        <button onclick="downloadToken()" 
                                class="bg-blue-600 text-white py-3 rounded-xl font-bold hover:bg-blue-700 transition flex items-center justify-center">
                            <i class="fas fa-download mr-2"></i>Download JSON
                        </button>
                    </div>
                </div>

                <!-- Loading -->
                <div id="loading" class="glass-morphism rounded-2xl p-8 mt-8 glow-border hidden">
                    <div class="text-center">
                        <div class="w-16 h-16 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
                        <h3 class="text-xl font-bold text-white mb-2">Generating  Token</h3>
                        <p class="text-gray-400">Please wait while we securely generate your token...</p>
                    </div>
                </div>

                <!-- Error Display -->
                <div id="error" class="glass-morphism rounded-2xl p-8 mt-8 border border-red-500/30 hidden">
                    <div class="text-center">
                        <i class="fas fa-exclamation-triangle text-red-400 text-4xl mb-4"></i>
                        <h3 class="text-xl font-bold text-red-300 mb-2">Token Generation Failed</h3>
                        <p id="errorMessage" class="text-red-200"></p>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- Statistics Section -->
    <section id="stats" class="py-20">
        <div class="container mx-auto px-4">
            <div class="text-center mb-16">
                <h2 class="text-4xl font-bold text-white mb-4">Live Statistics</h2>
                <p class="text-xl text-gray-400 max-w-2xl mx-auto">
                    Real-time performance metrics of our token generation service.
                </p>
            </div>
            
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <div class="glass-morphism rounded-2xl p-6 text-center hover:transform hover:-translate-y-2 transition-all duration-300">
                    <div class="text-4xl font-bold text-white mb-2" id="totalRequests">0</div>
                    <div class="text-gray-400">Total Requests</div>
                    <div class="mt-4 w-full bg-gray-700 rounded-full h-2">
                        <div class="bg-indigo-500 h-2 rounded-full" style="width: 100%"></div>
                    </div>
                </div>
                
                <div class="glass-morphism rounded-2xl p-6 text-center hover:transform hover:-translate-y-2 transition-all duration-300">
                    <div class="text-4xl font-bold text-white mb-2" id="successfulLogins">0</div>
                    <div class="text-gray-400">Successful Logins</div>
                    <div class="mt-4 w-full bg-gray-700 rounded-full h-2">
                        <div class="bg-green-500 h-2 rounded-full" style="width: 95%"></div>
                    </div>
                </div>
                
                <div class="glass-morphism rounded-2xl p-6 text-center hover:transform hover:-translate-y-2 transition-all duration-300">
                    <div class="text-4xl font-bold text-white mb-2" id="failedLogins">0</div>
                    <div class="text-gray-400">Failed Logins</div>
                    <div class="mt-4 w-full bg-gray-700 rounded-full h-2">
                        <div class="bg-red-500 h-2 rounded-full" style="width: 5%"></div>
                    </div>
                </div>
                
                <div class="glass-morphism rounded-2xl p-6 text-center hover:transform hover:-translate-y-2 transition-all duration-300">
                    <div class="text-4xl font-bold text-white mb-2" id="avgResponseTime">0ms</div>
                    <div class="text-gray-400">Avg Response Time</div>
                    <div class="mt-4 w-full bg-gray-700 rounded-full h-2">
                        <div class="bg-cyan-500 h-2 rounded-full" style="width: 85%"></div>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- Footer -->
    <footer class="glass-morphism border-t border-gray-800 py-12">
        <div class="container mx-auto px-4">
            <div class="flex flex-col md:flex-row justify-between items-center">
                <div class="mb-6 md:mb-0">
                    <div class="flex items-center space-x-2 mb-4">
                        <i class="fas fa-rocket text-2xl text-indigo-400"></i>
                        <span class="text-xl font-bold gradient-text">Token</span>
                    </div>
                    <p class="text-gray-400 max-w-md">
                        Advanced Free Fire token generation service with  features and military-grade security.
                    </p>
                </div>
                
                <div class="flex space-x-6">
                    <a href="#" class="text-gray-400 hover:text-indigo-400 transition-colors">
                        <i class="fab fa-github text-xl"></i>
                    </a>
                    <a href="#" class="text-gray-400 hover:text-indigo-400 transition-colors">
                        <i class="fab fa-discord text-xl"></i>
                    </a>
                    <a href="#" class="text-gray-400 hover:text-indigo-400 transition-colors">
                        <i class="fab fa-telegram text-xl"></i>
                    </a>
                    <a href="#" class="text-gray-400 hover:text-indigo-400 transition-colors">
                        <i class="fab fa-twitter text-xl"></i>
                    </a>
                </div>
            </div>
            
            <div class="border-t border-gray-800 mt-8 pt-8 text-center text-gray-500 text-sm">
                <p>&copy; 2023 Token. All rights reserved. This service is not affiliated with Garena Free Fire.</p>
            </div>
        </div>
    </footer>

    <script>
        // Create animated background particles
        function createParticles() {
            const container = document.getElementById('particles-container');
            const particleCount = 50;
            
            for (let i = 0; i < particleCount; i++) {
                const particle = document.createElement('div');
                particle.classList.add('particle');
                
                // Random properties
                const size = Math.random() * 5 + 1;
                const posX = Math.random() * 100;
                const posY = Math.random() * 100;
                const delay = Math.random() * 20;
                const duration = Math.random() * 10 + 10;
                
                particle.style.width = `${size}px`;
                particle.style.height = `${size}px`;
                particle.style.left = `${posX}%`;
                particle.style.top = `${posY}%`;
                particle.style.animation = `float ${duration}s ease-in-out ${delay}s infinite`;
                
                container.appendChild(particle);
            }
        }
        
        // Update stats
        async function updateStats() {
            try {
                const response = await fetch('/api/stats');
                const data = await response.json();
                document.getElementById('totalRequests').textContent = data.total_requests.toLocaleString();
                document.getElementById('successfulLogins').textContent = data.successful_logins.toLocaleString();
                document.getElementById('failedLogins').textContent = data.failed_logins.toLocaleString();
                document.getElementById('avgResponseTime').textContent = data.avg_response_time + 'ms';
            } catch (error) {
                console.error('Failed to update stats:', error);
            }
        }
        
        // Generate token
        async function generateToken() {
            const uid = document.getElementById('uid').value;
            const password = document.getElementById('password').value;
            
            if (!uid || !password) {
                showError('Please enter both UID and Password');
                return;
            }

            showLoading();
            hideResult();
            hideError();

            try {
                const response = await fetch(`/token?uid=${encodeURIComponent(uid)}&password=${encodeURIComponent(password)}`);
                const data = await response.json();
                
                if (response.ok) {
                    showResult(data);
                } else {
                    showError(data.detail || 'Failed to generate token');
                }
            } catch (error) {
                showError('Network error: ' + error.message);
            } finally {
                hideLoading();
                updateStats();
            }
        }
        
        // UI functions
        function showLoading() {
            document.getElementById('loading').classList.remove('hidden');
        }

        function hideLoading() {
            document.getElementById('loading').classList.add('hidden');
        }

        function showResult(data) {
            document.getElementById('resultData').textContent = JSON.stringify(data, null, 2);
            document.getElementById('result').classList.remove('hidden');
        }

        function hideResult() {
            document.getElementById('result').classList.add('hidden');
        }

        function showError(message) {
            document.getElementById('errorMessage').textContent = message;
            document.getElementById('error').classList.remove('hidden');
        }

        function hideError() {
            document.getElementById('error').classList.add('hidden');
        }

        function copyToClipboard() {
            const data = document.getElementById('resultData').textContent;
            navigator.clipboard.writeText(data).then(() => {
                // Show success notification
                const button = event.target;
                const originalText = button.innerHTML;
                button.innerHTML = '<i class="fas fa-check mr-2"></i>Copied!';
                button.classList.remove('bg-green-600');
                button.classList.add('bg-green-700');
                
                setTimeout(() => {
                    button.innerHTML = originalText;
                    button.classList.remove('bg-green-700');
                    button.classList.add('bg-green-600');
                }, 2000);
            });
        }

        function downloadToken() {
            const data = document.getElementById('resultData').textContent;
            const blob = new Blob([data], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'freefire_token.json';
            a.click();
            URL.revokeObjectURL(url);
        }
        
        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            createParticles();
            updateStats();
            setInterval(updateStats, 5000);
            
            // Add scroll animations
            const observerOptions = {
                threshold: 0.1,
                rootMargin: '0px 0px -50px 0px'
            };
            
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('animate-fade-in');
                    }
                });
            }, observerOptions);
            
            // Observe all sections
            document.querySelectorAll('section').forEach(section => {
                observer.observe(section);
            });
        });
    </script>
</body>
</html>
"""

async def get_token_async(password: str, uid: str):
    """Async token acquisition with better error handling"""
    start_time = time.time()
    try:
        session = await _service.get_session()
        url = "https://100067.connect.garena.com/oauth/guest/token/grant"
        headers = {
            "Host": "100067.connect.garena.com",
            "User-Agent": "GarenaMSDK/4.0.19P4(G011A ;Android 9;en;US;)",
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept-Encoding": "gzip",
        }
        data = {
            "uid": uid,
            "password": password,
            "response_type": "token",
            "client_type": "2",
            "client_secret": "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3",
            "client_id": "100067"
        }
        
        async with session.post(url, headers=headers, data=data, ssl=False) as response:
            if response.status == 200:
                token_json = await response.json()
                if "access_token" in token_json and "open_id" in token_json:
                    stats['successful_logins'] += 1
                    return token_json
                else:
                    print(f"Token response missing required fields: {token_json}")
            
            stats['failed_logins'] += 1
            return None
            
    except Exception as e:
        print(f"Token acquisition error: {e}")
        stats['failed_logins'] += 1
        return None
    finally:
        response_time = int((time.time() - start_time) * 1000)
        stats['total_requests'] += 1
        # Update average response time
        if stats['total_requests'] == 1:
            stats['avg_response_time'] = response_time
        else:
            stats['avg_response_time'] = (
                (stats['avg_response_time'] * (stats['total_requests'] - 1)) + response_time
            ) / stats['total_requests']

def prepare_major_login(token_data: dict):
    """Prepare MajorLogin object with fallback values"""
    if not PROTOBUF_AVAILABLE:
        raise Exception("Protobuf modules not available")
    
    try:
        major_login = MajorLoginReq_pb2.MajorLogin()
        major_login.event_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        major_login.game_name = "free fire"
        major_login.platform_id = 1
        major_login.client_version = "2.112.2"
        major_login.system_software = "Android OS 9 / API-28"
        major_login.system_hardware = "Handheld"
        major_login.telecom_operator = "Verizon"
        major_login.network_type = "WIFI"
        major_login.screen_width = 1920
        major_login.screen_height = 1080
        major_login.screen_dpi = "280"
        major_login.processor_details = "ARM64 FP ASIMD AES VMH | 2865 | 4"
        major_login.memory = 3003
        major_login.gpu_renderer = "Adreno (TM) 640"
        major_login.gpu_version = "OpenGL ES 3.1 v1.46"
        major_login.unique_device_id = f"Google|{uuid.uuid4()}"
        major_login.client_ip = "223.191.51.89"
        major_login.language = "en"
        major_login.open_id = token_data.get('open_id', '')
        major_login.open_id_type = "4"
        major_login.device_type = "Handheld"
        
        # Set memory available if the field exists
        if hasattr(major_login, 'memory_available'):
            memory_available = major_login.memory_available
            if hasattr(memory_available, 'version'):
                memory_available.version = 55
            if hasattr(memory_available, 'hidden_value'):
                memory_available.hidden_value = 81
        
        major_login.access_token = token_data.get('access_token', '')
        major_login.platform_sdk_id = 1
        major_login.network_operator_a = "Verizon"
        major_login.network_type_a = "WIFI"
        
        # Only set fields that exist in the protobuf
        optional_fields = {
            'client_using_version': "7428b253defc164018c604a1ebbfebdf",
            'external_storage_total': 36235,
            'external_storage_available': 31335,
            'internal_storage_total': 2519,
            'internal_storage_available': 703,
            'login_by': 3,
            'channel_type': 3,
            'cpu_type': 2,
            'cpu_architecture': "64",
            'client_version_code': "2019117863",
            'graphics_api': "OpenGLES2",
            'login_open_id_type': 4,
            'loading_time': 13564,
            'release_channel': "android",
            'if_push': 1,
            'is_vpn': 1,
            'origin_platform_type': "4",
            'primary_platform_type': "4"
        }
        
        for field, value in optional_fields.items():
            if hasattr(major_login, field):
                setattr(major_login, field, value)
        
        return major_login
    except Exception as e:
        raise Exception(f"Failed to prepare MajorLogin: {e}")

def parse_response(content):
    """Parse JWT response with error handling"""
    try:
        response_dict = {}
        if hasattr(content, 'decode'):
            content = content.decode('utf-8', errors='ignore')
        
        lines = str(content).split("\n")
        for line in lines:
            if ":" in line:
                key, value = line.split(":", 1)
                response_dict[key.strip()] = value.strip().strip('"')
        return response_dict
    except Exception as e:
        print(f"Response parsing error: {e}")
        return {}

@app.route('/')
def ui():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/stats')
def get_stats():
    return jsonify(stats)

@app.route('/token')
def get_token():
    """Free Fire token generation endpoint"""
    uid = request.args.get('uid')
    password = request.args.get('password')
    
    if not uid or not password:
        return jsonify({'error': 'UID and password are required'}), 400
    
    if not PROTOBUF_AVAILABLE:
        return jsonify({'error': 'Protobuf modules not available. Please check server logs.'}), 500
    
    # Run async function
    token_data = asyncio.run(get_token_async(password, uid))
    if not token_data:
        return jsonify({'error': 'Invalid UID or password. Please check your credentials.'}), 401
    
    try:
        # Prepare MajorLogin
        major_login = prepare_major_login(token_data)
        serialized = major_login.SerializeToString()
        encrypted = _service.encrypt_message(serialized)
        edata = binascii.hexlify(encrypted).decode()

        headers = {
            'User-Agent': "Dalvik/2.1.0 (Linux; Android 9)",
            'Connection': "Keep-Alive",
            'Accept-Encoding': "gzip",
            'Content-Type': "application/octet-stream",
            'X-Unity-Version': "2018.4.11f1",
            'X-GA': "v1 1",
            'ReleaseVersion': "OB51"
        }

        # Send MajorLogin async
        async def send_major_login():
            session = await _service.get_session()
            async with session.post(
                "https://loginbp.common.ggbluefox.com/MajorLogin",
                data=bytes.fromhex(edata),
                headers=headers,
                ssl=False
            ) as response:
                if response.status == 200:
                    return await response.read()
                else:
                    raise Exception(f"MajorLogin failed with status: {response.status}")
        
        content = asyncio.run(send_major_login())
        
        # Parse MajorLoginRes
        login_res = MajorLoginRes_pb2.MajorLoginRes()
        login_res.ParseFromString(content)

        # Parse JWT
        jwt_msg = jwt_generator_pb2.Garena_420()
        jwt_msg.ParseFromString(content)
        jwt_dict = parse_response(str(jwt_msg))
        token = jwt_dict.get("token", "")

        # Build response
        response_data = {
            "accountId": getattr(login_res, 'account_id', ''),
            "tokenStatus": jwt_dict.get("status", "valid"),
            "token": token,
            "ttl": getattr(login_res, 'ttl', 86400),
            "serverUrl": getattr(login_res, 'server_url', ""),
            "expireAt": int(time.time()) + getattr(login_res, 'ttl', 86400),
            "generatedAt": datetime.now().isoformat(),
            "premium": True,
            "status": "success",
            "uid": uid
        }

        return jsonify(response_data)

    except Exception as e:
        print(f"Token generation error: {e}")
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0",
        "stats": stats,
        "protobuf_available": PROTOBUF_AVAILABLE,
        "environment": os.getenv("VERCEL_ENV", "development")
    })

@app.route('/test')
def test_endpoint():
    """Test endpoint to verify API is working"""
    return jsonify({
        "message": "API is working!",
        "timestamp": datetime.now().isoformat(),
        "status": "success"
    })

# Startup and shutdown events
@app.first_request
async def startup():
    await _service.get_session()
    print("🚀 Free Fire Token Service Started Successfully!")
    print(f"📊 Protobuf Available: {PROTOBUF_AVAILABLE}")
    print("🔧 API Ready for Requests")

@app.teardown_appcontext
async def shutdown(error=None):
    await _service.close_session()

if __name__ == '__main__':
    port = int(os.getenv("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
