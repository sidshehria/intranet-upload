const express = require('express');
const { MongoClient } = require('mongodb');
const multer = require('multer');
const fs = require('fs');
const path = require('path');
const pdfParse = require('pdf-parse');
const { Configuration, OpenAIApi } = require('openai');
const app = express();
const PORT = 3000;

const uri = 'mongodb://localhost:27017/';
const client = new MongoClient(uri);

// Set up multer for file uploads
const upload = multer({ dest: 'uploads/' });

// Setup OpenAI API client
const configuration = new Configuration({
    apiKey: 'AIzaSyD9rynFL9dTAOo-1FgKu1X8inOaU76ZJtM',
});
const openai = new OpenAIApi(configuration);

async function connectClient() {
    try {
        await client.connect();
        console.log('Connected successfully to MongoDB');
    } catch (error) {
        console.error('Error connecting to MongoDB:', error);
        process.exit(1);
    }
}

async function getDataFromDB() {
    const database = client.db('mytesting_db');
    const collection = database.collection('testing_db');
    const data = await collection.find({}).toArray();
    return data;
}

app.get('/api/documents', async (req, res) => {
    try {
        const data = await getDataFromDB();
        res.json(data);
    } catch (error) {
        console.error(error);
        res.status(500).send('Error fetching data');
    }
});

app.post('/api/upload', upload.single('file'), async (req, res) => {
    try {
        if (!req.file) {
            return res.status(400).send('No file uploaded');
        }

        const filePath = req.file.path;
        const fileName = req.file.originalname;

        const dataBuffer = fs.readFileSync(filePath);
        const pdfData = await pdfParse(dataBuffer);

        const prompt = `Extract all data from the following technical document text into a structured JSON format with all parameters and their values:\n\n${pdfData.text}`;

        const completion = await openai.createChatCompletion({
            model: "gpt-4",
            messages: [
                { role: "system", content: "You are a helpful assistant that extracts structured JSON data from technical document text." },
                { role: "user", content: prompt }
            ],
            temperature: 0,
            max_tokens: 2000
        });

        const jsonResponseText = completion.data.choices[0].message.content;

        let jsonData;
        try {
            jsonData = JSON.parse(jsonResponseText);
        } catch (parseError) {
            console.error('Error parsing JSON from OpenAI response:', parseError);
            return res.status(500).send('Error parsing JSON from OpenAI response');
        }

        // Save JSON file to uploads/json folder
        const jsonDir = path.join(__dirname, 'uploads', 'json');
        if (!fs.existsSync(jsonDir)) {
            fs.mkdirSync(jsonDir, { recursive: true });
        }
        const jsonFilePath = path.join(jsonDir, fileName + '.json');
        fs.writeFileSync(jsonFilePath, JSON.stringify(jsonData, null, 2));

        // Save JSON data to MongoDB
        const database = client.db('mytesting_db');
        const collection = database.collection('testing_db');
        await collection.insertOne(jsonData);

        // Delete the uploaded PDF file after processing
        fs.unlinkSync(filePath);

        res.status(200).json({ message: 'File processed and data saved successfully', data: jsonData });
    } catch (error) {
        console.error('Error processing file:', error);
        res.status(500).send('Error processing file');
    }
});

// If this script is run directly, run the conversion function
if (require.main === module) {
    connectClient().then(() => {
        app.listen(PORT, () => {
            console.log(`API server running at http://localhost:${PORT}`);
        });
    });
}

process.on('SIGINT', async () => {
    try {
        await client.close();
        console.log('MongoDB client closed');
        process.exit(0);
    } catch (error) {
        console.error('Error closing MongoDB client:', error);
        process.exit(1);
    }
});
