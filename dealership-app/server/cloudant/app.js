const express = require("express");
const mongoose = require("mongoose");
const Dealership = require("./models/dealership.js");
const Review = require("./models/reviews.js");
const dealershipsData = require("./data/dealerships.json");
const reviewsData = require("./data/reviews.json");

const app = express();
app.use(express.json());

// MongoDB connection configuration
const MONGODB_URI = "mongodb://mongo:27017/dealershipsDB";
const mongooseOptions = {
  useNewUrlParser: true,
  useUnifiedTopology: true,
  serverSelectionTimeoutMS: 5000,
  socketTimeoutMS: 45000,
};

// Connect to MongoDB with retry logic
const connectWithRetry = () => {
  mongoose
    .connect(MONGODB_URI, mongooseOptions)
    .then(() => {
      console.log("✅ Connected to MongoDB");

      // Start server ONLY after successful connection
      app.listen(PORT, () => {
        console.log(`🚀 Server running on port ${PORT}`);
        loadInitialData(); // Load data after server starts
      });
    })
    .catch((err) => {
      console.error(`❌ MongoDB connection failed: ${err.message}`);
      console.log("🔄 Retrying connection in 5 seconds...");
      setTimeout(connectWithRetry, 5000);
    });
};

// Load initial data (with connection check)
const loadInitialData = async () => {
  try {
    // Verify connection is established
    if (mongoose.connection.readyState !== 1) {
      throw new Error("MongoDB connection not ready");
    }

    console.log("🔄 Clearing existing data...");
    await Dealership.deleteMany({});
    await Review.deleteMany({});

    console.log("📥 Inserting initial data...");
    await Dealership.insertMany(dealershipsData.dealerships);
    await Review.insertMany(reviewsData.reviews);

    console.log("✅ Initial data loaded successfully");
  } catch (error) {
    console.error("❌ Error loading initial data:", error.message);
  }
};

// API Endpoints
app.get("/fetchReviews", async (req, res) => {
  try {
    const reviews = await Review.find().maxTimeMS(15000);
    res.json(reviews);
  } catch (error) {
    res.status(500).json({
      message: `Failed to fetch reviews: ${error.message}`,
    });
  }
});

app.get("/fetchReviews/dealer/:id", async (req, res) => {
  try {
    const reviews = await Review.find({ dealership: req.params.id }).maxTimeMS(
      15000,
    );
    res.json(reviews);
  } catch (error) {
    res.status(500).json({
      message: `Failed to fetch reviews for dealer ${req.params.id}: ${error.message}`,
    });
  }
});

app.get("/fetchDealers", async (req, res) => {
  try {
    const dealerships = await Dealership.find().maxTimeMS(15000);
    res.json(dealerships);
  } catch (error) {
    res.status(500).json({
      message: `Failed to fetch dealerships: ${error.message}`,
    });
  }
});

app.get("/fetchDealers/:state", async (req, res) => {
  try {
    const dealerships = await Dealership.find({
      state: req.params.state,
    }).maxTimeMS(15000);
    res.json(dealerships);
  } catch (error) {
    res.status(500).json({
      message: `Failed to fetch dealers in ${req.params.state}: ${error.message}`,
    });
  }
});

app.get("/fetchDealer/:id", async (req, res) => {
  try {
    const dealership = await Dealership.findOne({
      id: req.params.id,
    }).maxTimeMS(15000);
    res.json(dealership);
  } catch (error) {
    res.status(500).json({
      message: `Failed to fetch dealer ${req.params.id}: ${error.message}`,
    });
  }
});

app.post("/insert_review", async (req, res) => {
  try {
    const newReview = new Review(req.body);
    await newReview.save();
    res.status(201).json(newReview);
  } catch (error) {
    res.status(400).json({
      message: `Failed to create review: ${error.message}`,
    });
  }
});

const PORT = 3000;

// Start the connection process
connectWithRetry();

// Handle shutdown gracefully
process.on("SIGINT", async () => {
  console.log("\n🛑 Shutting down gracefully...");
  await mongoose.connection.close();
  process.exit(0);
});
