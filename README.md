# pgen

A powerful and feature-rich Python application for generating realistic personal data for testing and development purposes. This tool creates comprehensive datasets including personal information, addresses, employment details, social media profiles, and more.

## 🌟 Features

### Core Functionality
- **Multi-format Export**: Generate data in TXT, HTML, JSON, CSV formats
- **Realistic Data Generation**: Create believable personal information with Russian context
- **Family Generation**: Generate family groups with shared surnames
- **Enhanced Generation**: Improved data quality with categorized professions and detailed profiles
- **ChatGPT Integration**: Optional AI-powered data enhancement (requires OpenAI API key)

### Data Types Generated
- Personal information (name, surname, patronymic, birth date)
- Contact details (phone, address, email)
- Employment data (company, position, salary)
- Social media profiles
- Financial data (loans, banking)
- Legal records (criminal cases, border crossings)
- Medical information (insurance, prescriptions)
- Real estate and property data

### Export Formats
- Single file (TXT, HTML, JSON, CSV, Real Database TXT, Enhanced TXT)
- Separate files for each record
- Real database simulation format
- Customizable output structure

## 🚀 Installation

### Prerequisites
- Python 3.7+
- Required packages (install via pip):

```bash
pip install tkinter pillow requests openai
```

### Running the Application

1. Clone or download the repository
2. Ensure all required dependencies are installed
3. Run the application:

```bash
python pgen.py
```

## 🛠️ Usage

### Basic Generation
1. Set the number of records to generate
2. Configure gender distribution (random, male-heavy, female-heavy)
3. Adjust probability sliders for different data types
4. Select output format
5. Click "Generate Data"

### Advanced Features

#### Enhanced Generation
- Enable "Use enhanced generation" for higher quality data
- Includes categorized professions (IT, Medicine, Finance, Education, Trade)
- More realistic company names and job positions

#### ChatGPT Integration
1. Click "ChatGPT Settings"
2. Enter your OpenAI API key
3. Test the connection
4. Enable "Use ChatGPT" for AI-enhanced data generation

#### Real Database Simulation
- Generates data in formats mimicking real Russian databases
- Includes multiple database types (FOMS, Rosreestr, Border Control, etc.)
- Realistic field structures and data patterns

### Configuration Options

#### Probability Settings
- Job information
- Salary data
- Social media profiles
- Family generation
- Patronymics
- Service clients
- Border crossings
- Micro-loans
- Criminal cases

#### Output Settings
- File format selection
- Family grouping
- Photo inclusion (for HTML)
- Output folder selection

## 📁 Project Structure

```
pgen.py                 # Main application file
data/                   # Data directory (optional)
  ├── malenames.json    # Male names database
  ├── femalenames.json  # Female names database
  ├── surnames.json     # Surnames database
  ├── cities.json       # Cities database
  ├── streets.json      # Streets database
  └── words.json        # Company name components
```

## 🔧 Data Sources

The application uses built-in datasets but can load external JSON files from the `data/` directory:
- Male and female names
- Surnames
- Cities and streets
- Company name components

## 📊 Generated Data Fields

### Personal Information
- Full name (surname, name, patronymic)
- Passport data
- Birth date and place
- Gender
- Phone number

### Address Information
- City, street, house and apartment numbers
- Multiple address formats

### Professional Data
- Company name and type
- Job position and category
- Salary information

### Additional Data
- Social media profiles (VK, OK, Telegram, Instagram)
- Service subscriptions (Yandex.Taxi, banking, etc.)
- Border crossing records
- Loan information
- Criminal records
- Medical data and prescriptions

## 🎨 Interface Features

- **Theme Support**: Light, Dark, and Blue themes
- **Real-time Preview**: See generated data before export
- **History Tracking**: Keep track of generation sessions
- **Progress Indicators**: Status updates during generation
- **Responsive Design**: Adapts to different screen sizes

## ⚙️ Settings

### Name Settings
- Female surname format options

### Address Settings
- Customizable house number ranges
- Customizable apartment number ranges

## 📈 Statistics & History

- Tracks total generated records
- Stores generation parameters
- Export history with timestamps
- Session management

## 🔒 Privacy & Security

- All data is generated locally
- No external data transmission (except optional ChatGPT API calls)
- Generated data is fictional and for testing purposes only

## 🐛 Troubleshooting

### Common Issues

1. **Missing Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **ChatGPT Connection Issues**
   - Verify API key validity
   - Check internet connection
   - Ensure sufficient API credits

3. **File Permission Errors**
   - Run as administrator if needed
   - Check output folder permissions

### Performance Tips
- For large datasets (>1000 records), use single file formats
- Disable enhanced generation for faster performance
- Reduce probability sliders for less complex data

## 📄 License

This project is intended for educational and testing purposes. Generated data should not be used for illegal activities.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review existing GitHub issues
3. Create a new issue with detailed description

---

**Note**: This tool generates fictional data for testing and development purposes only. Do not use generated data for illegal activities or misrepresentation.
