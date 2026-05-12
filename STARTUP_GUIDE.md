# Quant Forge - Startup Guide

## Quick Start (Development Mode)

### Terminal 1 - Start Backend API
```bash
cd backend
npm run dev
```
This will start the Flask API server on `http://localhost:5000`

The API will automatically reload when you modify Python files.

### Terminal 2 - Start Frontend UI  
```bash
cd frontend
npm run dev
```
This will start the React development server on `http://localhost:5173`

The UI will automatically reload when you modify React/CSS files.

**The frontend will automatically open in your browser!**

---

## What You'll See

### Backend Console
```
 * Running on http://127.0.0.1:5000
 * Debugger is active!
```

### Frontend Console
```
VITE v5.4.21  ready in 234 ms

➜  Local:   http://localhost:5173/
➜  Press q to quit
```

---

## API Endpoints Available

- **GET** `/` - API info
- **GET** `/health` - Health check
- **GET** `/strategies` - List available strategies
- **POST** `/backtest` - Run a backtest
- **POST** `/optimize` - Optimize parameters

---

## Features Now Working

✅ **Semantic Clarity**
- Position shows "Shares Held" (not ambiguous units)
- SELL/SHORT fixed to "IN POSITION" / "NO POSITION" (long-only strategy)
- Long-only strategy clearly documented in trade log

✅ **Date Range Flexibility** 
- Date picker in the UI (default: 5-year history)
- Test any time period (2016-2022, 2020-2021, 2022 only, etc.)
- Both backtest and optimize support custom date ranges

✅ **Initial Capital**
- Configurable portfolio starting amount ($1k - $1M)
- All results scale correctly with capital

✅ **5 Trading Strategies**
1. Momentum
2. Mean Reversion
3. RSI
4. MACD
5. Bollinger Bands

✅ **Parameter Optimization**
- Grid-search across parameter ranges
- Returns top N results ranked by Sharpe ratio

---

## Troubleshooting

### Backend won't start
```bash
# Install dependencies
pip install flask flask-cors pandas yfinance numpy

# Try again
npm run dev
```

### Frontend shows "Cannot connect to API"
- Make sure backend is running on port 5000
- Check that `.env` file exists in frontend folder
- Verify `VITE_API_URL=http://localhost:5000` is set
This will start the Flask API server on `http://localhost:5002`

### Backend Console
```
 * Running on http://127.0.0.1:5002
 * Debugger is active!
```

### Frontend shows "Cannot connect to API"
- Make sure backend is running on port 5002
- Check that `.env` file exists in frontend folder
- Verify `VITE_API_URL=http://localhost:5002` is set

### Port already in use
```bash
# Kill process on port 5000
lsof -ti:5000 | xargs kill -9

# Kill process on port 5173
lsof -ti:5173 | xargs kill -9
```

---

## Development Tips

- Modify Python files → Flask auto-reloads
- Modify React files → Vite hot-reloads
- Check browser console for frontend errors
- Check terminal for backend logs

---

**Ready to backtest? Let's go! 🚀**
