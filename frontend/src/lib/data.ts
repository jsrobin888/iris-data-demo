import fs from 'fs';
import path from 'path';
import Papa from 'papaparse';

interface IrisRow {
  sepal_length: string;
  sepal_width: string;
  petal_length: string;
  petal_width: string;
  species: string;
}

// Sample Iris data if CSV doesn't exist
const sampleData = {
  setosa: [
    { sepal_length: 5.1, sepal_width: 3.5, petal_length: 1.4, petal_width: 0.2 },
    { sepal_length: 4.9, sepal_width: 3.0, petal_length: 1.4, petal_width: 0.2 },
    { sepal_length: 4.7, sepal_width: 3.2, petal_length: 1.3, petal_width: 0.2 },
    { sepal_length: 4.6, sepal_width: 3.1, petal_length: 1.5, petal_width: 0.2 },
    { sepal_length: 5.0, sepal_width: 3.6, petal_length: 1.4, petal_width: 0.2 },
    { sepal_length: 5.4, sepal_width: 3.9, petal_length: 1.7, petal_width: 0.4 },
    { sepal_length: 4.6, sepal_width: 3.4, petal_length: 1.4, petal_width: 0.3 },
    { sepal_length: 5.0, sepal_width: 3.4, petal_length: 1.5, petal_width: 0.2 },
    { sepal_length: 4.4, sepal_width: 2.9, petal_length: 1.4, petal_width: 0.2 },
    { sepal_length: 4.9, sepal_width: 3.1, petal_length: 1.5, petal_width: 0.1 }
  ],
  virginica: [
    { sepal_length: 6.3, sepal_width: 3.3, petal_length: 6.0, petal_width: 2.5 },
    { sepal_length: 5.8, sepal_width: 2.7, petal_length: 5.1, petal_width: 1.9 },
    { sepal_length: 7.1, sepal_width: 3.0, petal_length: 5.9, petal_width: 2.1 },
    { sepal_length: 6.3, sepal_width: 2.9, petal_length: 5.6, petal_width: 1.8 },
    { sepal_length: 6.5, sepal_width: 3.0, petal_length: 5.8, petal_width: 2.2 },
    { sepal_length: 7.6, sepal_width: 3.0, petal_length: 6.6, petal_width: 2.1 },
    { sepal_length: 4.9, sepal_width: 2.5, petal_length: 4.5, petal_width: 1.7 },
    { sepal_length: 7.3, sepal_width: 2.9, petal_length: 6.3, petal_width: 1.8 },
    { sepal_length: 6.7, sepal_width: 2.5, petal_length: 5.8, petal_width: 1.8 },
    { sepal_length: 7.2, sepal_width: 3.6, petal_length: 6.1, petal_width: 2.5 }
  ]
};

// Legacy function - now data is fetched from Python API
export function getIrisData(species: 'setosa' | 'virginica') {
  try {
    // Try to read from CSV file first
    const csvPath = path.join(process.cwd(), 'iris.csv');
    
    if (fs.existsSync(csvPath)) {
      const csvData = fs.readFileSync(csvPath, 'utf8');
      const parsed = Papa.parse<IrisRow>(csvData, { header: true, dynamicTyping: true });
      
      const filteredData = parsed.data.filter(row => row.species === species);
      
      return {
        sepal_length: filteredData.map(row => parseFloat(row.sepal_length)),
        sepal_width: filteredData.map(row => parseFloat(row.sepal_width)),
        petal_length: filteredData.map(row => parseFloat(row.petal_length)),
        petal_width: filteredData.map(row => parseFloat(row.petal_width)),
        species
      };
    }
  } catch (error) {
    console.error('Error reading CSV:', error);
  }
  
  // Fallback to sample data
  const data = sampleData[species];
  return {
    sepal_length: data.map(row => row.sepal_length),
    sepal_width: data.map(row => row.sepal_width),
    petal_length: data.map(row => row.petal_length),
    petal_width: data.map(row => row.petal_width),
    species
  };
}