# ArgusAI Test Routes - Panvel to Vashi Coverage

This document provides 10 test routes covering different areas of the Panvel-Vashi region for testing the ArgusAI safe routing system.

## Route 1: Central Panvel to Vashi Node
**Origin:** Panvel Railway Station  
**Destination:** Vashi Railway Station  
```
Origin: 18.9894, 73.1175
Destination: 19.0771, 72.9988
```
**Description:** Main arterial route through the city center

---

## Route 2: Panvel East to Vashi Sector 17
**Origin:** Panvel (East) - Khanda Colony  
**Destination:** Vashi Sector 17  
```
Origin: 19.0050, 73.1300
Destination: 19.0650, 72.9950
```
**Description:** Eastern approach with residential areas

---

## Route 3: Old Panvel to Sanpada
**Origin:** Old Panvel Market  
**Destination:** Sanpada Junction  
```
Origin: 18.9850, 73.1100
Destination: 19.0580, 73.0150
```
**Description:** Historic route through old town

---

## Route 4: Panvel Creek Bridge to Vashi Bridge
**Origin:** Panvel Creek Area  
**Destination:** Vashi Creek Bridge  
```
Origin: 18.9950, 73.1050
Destination: 19.0700, 73.0050
```
**Description:** Coastal route with bridge crossings

---

## Route 5: Khandeshwar to Turbhe
**Origin:** Khandeshwar Station  
**Destination:** Turbhe MIDC  
```
Origin: 19.0220, 73.0297
Destination: 19.0650, 73.0200
```
**Description:** Industrial corridor route

---

## Route 6: Panvel Highway to Vashi Highway
**Origin:** Panvel Highway Junction  
**Destination:** Vashi Palm Beach Road  
```
Origin: 18.9750, 73.1200
Destination: 19.0800, 72.9900
```
**Description:** High-speed highway route

---

## Route 7: South Panvel to Kopar Khairane
**Origin:** Panvel South - Kamothe Road  
**Destination:** Kopar Khairane Sector 10  
```
Origin: 18.9700, 73.1150
Destination: 19.0900, 73.0100
```
**Description:** Southern bypass route

---

## Route 8: Panvel MIDC to Vashi APMC
**Origin:** Panvel MIDC Area  
**Destination:** Vashi APMC Market  
```
Origin: 19.0100, 73.1250
Destination: 19.0550, 73.0000
```
**Description:** Commercial and market route

---

## Route 9: New Panvel to Nerul
**Origin:** New Panvel - Taloja Road  
**Destination:** Nerul Sector 20  
```
Origin: 19.0300, 73.1400
Destination: 19.0330, 73.0180
```
**Description:** New development area route

---

## Route 10: Panvel North to Vashi North
**Origin:** Panvel North - Kalamboli  
**Destination:** Vashi North - Airoli Bridge  
```
Origin: 19.0477, 73.0769
Destination: 19.0950, 73.0050
```
**Description:** Northern corridor with flyovers

---

## Quick Test Coordinates (Copy-Paste Ready)

### Short Routes (5-10 km)
```
Route A: 18.9894, 73.1175 → 19.0220, 73.0297
Route B: 19.0050, 73.1300 → 19.0477, 73.0769
Route C: 18.9850, 73.1100 → 19.0100, 73.1250
```

### Medium Routes (10-15 km)
```
Route D: 18.9750, 73.1200 → 19.0650, 73.0200
Route E: 19.0100, 73.1250 → 19.0580, 73.0150
Route F: 18.9950, 73.1050 → 19.0650, 72.9950
```

### Long Routes (15+ km)
```
Route G: 18.9700, 73.1150 → 19.0771, 72.9988
Route H: 19.0300, 73.1400 → 19.0800, 72.9900
Route I: 18.9894, 73.1175 → 19.0950, 73.0050
Route J: 18.9750, 73.1200 → 19.0900, 73.0100
```

---

## Testing Tips

1. **Test Different Times:** Try routes during rush hours (8-10 AM, 5-8 PM) vs off-peak
2. **Weather Conditions:** Test with different weather scenarios using the live conditions API
3. **Compare Safe vs Fast:** Always compare both routing modes to see safety improvements
4. **Check AI Proof:** Click "View Core AI Routing Proof" button to verify performance metrics
5. **Hazard Detection:** Look for pothole and crash markers along the routes

---

## API Testing Examples

### Using cURL
```bash
# Route comparison
curl "http://localhost:8001/api/route-comparison?origin_lat=18.9894&origin_lng=73.1175&dest_lat=19.0771&dest_lng=72.9988"

# Live conditions
curl "http://localhost:8001/api/live-conditions"

# Single safe route
curl "http://localhost:8001/api/safe-route?origin_lat=18.9894&origin_lng=73.1175&dest_lat=19.0220&dest_lng=73.0297&mode=safe"
```

### Using Frontend
1. Open ArgusAI web interface
2. Click on map to set origin (or use quick routes)
3. Click again to set destination
4. Click "FIND SAFE ROUTE" button
5. Review route comparison and click "View Core AI Routing Proof"

---

## Expected Results

Each route should display:
- ✅ Safe route (green) with lower danger score
- ✅ Fast route (red) with higher danger score
- ✅ Safety improvement percentage
- ✅ Hazard markers (potholes, crashes, blackspots)
- ✅ Live conditions (weather, traffic, air quality)
- ✅ AI routing proof with performance metrics
- ✅ Dynamic penalties based on conditions

---

## Coverage Map

```
        Vashi (North)
            ↑
    Nerul ← + → Airoli
            ↑
        Turbhe
            ↑
      Kopar Khairane
            ↑
        Sanpada
            ↑
      Khandeshwar
            ↑
    Panvel (Central)
       ↙    ↓    ↘
  West   South   East
```

---

**Last Updated:** 2026-04-14  
**Map Coverage:** Panvel-Vashi corridor (approx 20km × 15km)  
**Total Test Routes:** 10 major + 10 quick test routes
