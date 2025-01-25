const mongoose = require("mongoose");

const dealershipSchema = new mongoose.Schema({
    id: { type: Number, required: true, unique: true },
    city: { type: String, required: true },
    state: { type: String, required: true },
    st: { type: String, required: true },
    address: { type: String, required: true },
    zip: { type: String, required: true },
    lat: { type: Number, required: true },
    long: { type: Number, required: true },
    short_name: { type: String, required: true },
    full_name: { type: String, required: true },
});

const Dealership = mongoose.model("Dealership", dealershipSchema);

module.exports = Dealership;
