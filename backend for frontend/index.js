const express = require('express');
const cors = require('cors');
const { google } = require('googleapis');
const { exec } = require('child_process');
const path = require('path');

const app = express();
const port = 3001;

app.use(cors());
app.use(express.json());

const auth = new google.auth.GoogleAuth({
  keyFile: 'G:\\Programador JC\\automacaomake-424118-f166235a4ab7.json',
  scopes: ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/spreadsheets.readonly']
});

const sheets = google.sheets({ version: 'v4', auth });

const SPREADSHEET_ID = '1PEoLUkDpfKhPf6c4w_lcgjpbly9L3TrL3mWDHW1obhs';

app.get('/data/:sheetName', async (req, res) => {
  const sheetName = req.params.sheetName;
  try {
    const response = await sheets.spreadsheets.values.get({
      spreadsheetId: SPREADSHEET_ID,
      range: `${sheetName}!A1:Z1000`
    });
    res.json(response.data.values);
  } catch (error) {
    console.error('Error fetching data:', error);
    res.status(500).send('Error fetching data');
  }
});

app.post('/run-python', (req, res) => {
  const { directoryPath, downloadFolder } = req.body;

  console.log('Received directoryPath:', directoryPath);
  console.log('Received downloadFolder:', downloadFolder);

  const scriptPath = path.join(__dirname, '../backend/src/main.py');
  const command = `python "${scriptPath}" "${directoryPath}" "${downloadFolder}"`;

  console.log('Running command:', command);

  exec(command, (error, stdout, stderr) => {
    if (error) {
      console.error(`Error executing script: ${error.message}`);
      return res.status(500).send(`Error executing script: ${error.message}`);
    }
    if (stderr) {
      console.error(`Script error: ${stderr}`);
      return res.status(500).send(`Script error: ${stderr}`);
    }
    console.log(`Script output: ${stdout}`);
    res.send(`Script output: ${stdout}`);
  });
});

app.listen(port, () => {
  console.log(`Server is running on port ${port}`);
});
