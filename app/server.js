const express = require('express');
const { MongoClient } = require('mongodb');
const os = require('os');

const app = express();
app.use(express.json());
app.use(express.static('public')); // Frontend serve karne ke liye

const PORT = 80; // Kubernetes mein port 80 use hoga
const MONGO_URL = process.env.MONGO_URL || 'mongodb://localhost:27017/emidb';

let db;
let mongoClient;

// MongoDB Connect
async function connectDB() {
    try {
        mongoClient = new MongoClient(MONGO_URL);
        await mongoClient.connect();
        db = mongoClient.db();
        console.log("Connected to MongoDB");
    } catch (err) {
        console.error("MongoDB connection failed:", err.message);
    }
}
connectDB();

// API 1: Health Check
app.get('/health', async (req, res) => {
    try {
        await db.command({ ping: 1 });
        res.status(200).send("OK");
    } catch (err) {
        res.status(500).send("MongoDB not reachable");
    }
});

// API 2: Calculate EMI
app.post('/api/emi', async (req, res) => {
    try {
        let { principal, rate, months } = req.body;

        // Server-side validation
        principal = Number(principal);
        rate = Number(rate);
        months = Number(months);

        if (principal <= 0 || rate <= 0 || months <= 0) {
            return res.status(400).json({ error: "All inputs must be positive numbers." });
        }

        // EMI Formula: P * r * (1+r)^n / ((1+r)^n - 1)
        let r = rate / 12 / 100;
        let emi = (principal * r * Math.pow(1 + r, months)) / (Math.pow(1 + r, months) - 1);
        
        let totalPayment = emi * months;
        let totalInterest = totalPayment - principal;

        // Pod info
        let servedBy = process.env.HOSTNAME || os.hostname();
        let ip = req.ip || req.connection.remoteAddress;

        let record = {
            principal,
            rate,
            months,
            emi: Number(emi.toFixed(2)),
            servedBy,
            createdAt: new Date()
        };

        // Save to MongoDB
        if (db) {
            await db.collection('calculations').insertOne(record);
        }

        res.json({
            emi: Number(emi.toFixed(2)),
            totalPayment: Number(totalPayment.toFixed(2)),
            totalInterest: Number(totalInterest.toFixed(2)),
            servedBy: servedBy,
            ip: ip
        });

    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

// API 3: Get History
app.get('/api/history', async (req, res) => {
    try {
        if (!db) return res.status(500).json({ error: "DB not connected" });
        
        const history = await db.collection('calculations')
            .find()
            .sort({ createdAt: -1 })
            .limit(10)
            .toArray();
            
        res.json(history);
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});
