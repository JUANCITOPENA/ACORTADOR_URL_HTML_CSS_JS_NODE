const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
const dotenv = require('dotenv');
dotenv.config();

const app = express();
const port = process.env.PORT || 4000;
const domain = process.env.DOMAIN;

// Middleware para servir archivos estáticos
app.use(express.static('public'));

// Middleware para analizar el cuerpo de las solicitudes JSON
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Middleware para CORS
app.use(cors({
    origin: domain,
    optionsSuccessStatus: 200
}));

// Conexión a MongoDB
mongoose.connect(process.env.MONGO_URI, { useNewUrlParser: true, useUnifiedTopology: true })
  .then(() => console.log('Conectado a MongoDB'))
  .catch(err => console.error(err));

// Definir esquema y modelo para URLs
const urlSchema = new mongoose.Schema({
    longUrl: String,
    shortUrlId: String,
    date: { type: Date, default: Date.now }
});

const Url = mongoose.model('Url', urlSchema);

// Endpoint para acortar URL
app.post('/api/shorten', async (req, res) => {
    console.log(req.body);
    const { longUrl } = req.body;
    const uniqueId = Math.random().toString(36).substring(2, 8);
    
    const newUrl = new Url({ longUrl, shortUrlId: uniqueId });
    await newUrl.save();
    
    const shortUrl = `${domain}/short.url/${uniqueId}`;
    res.json({ longUrl, shortUrl });
});

// Endpoint para redirigir a URL original
app.get('/short.url/:id', async (req, res) => {
    console.log(req.params.id);
    const url = await Url.findOne({ shortUrlId: req.params.id });
    if (url) {
        console.log(url.longUrl);
        res.redirect(url.longUrl);
    } else {
        res.status(404).send('URL no encontrada');
    }
});

// Ruta para servir el archivo HTML principal
app.get('/', (req, res) => {
    res.sendFile(__dirname + '/public/index.html');
});

app.listen(port, () => console.log(`Servidor corriendo en el puerto ${port}`));
