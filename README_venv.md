# הגדרת סביבה וירטואלית לפרוייקט DMTS_olfacto

## יצירת והפעלת הסביבה הוירטואלית

### יצירה (צריך לעשות רק פעם אחת):
```powershell
py -m venv .venv
```

### הפעלה (בכל פעם שפותחים את Cursor):
```powershell
.\.venv\Scripts\Activate.ps1
```

### כביה של הסביבה:
```powershell
deactivate
```

## התקנת תלויות

אחרי הפעלת הסביבה הוירטואלית:
```powershell
pip install -r requirements.txt
```

## בדיקת סטטוס הסביבה

### בדיקה שהסביבה פעילה:
```powershell
where python
```
אמור להציג נתיב שמכיל `.venv`

### רשימת חבילות מותקנות:
```powershell
pip list
```

## הערות חשובות

1. **RPi.GPIO** - החבילה מוערת ב-requirements.txt כיוון שהיא עובדת רק על Raspberry Pi
2. הסביבה הוירטואלית שמורה בתיקייה `.venv` ולא נכללת בגיט
3. כדי לעבוד עם הפרוייקט, צריך תמיד להפעיל את הסביבה הוירטואלית קודם
4. ב-Cursor, השורה תתחיל ב-`(.venv)` כשהסביבה פעילה

## הרצת הפרוייקט

אחרי הפעלת הסביבה הוירטואלית:
```powershell
python experiment.py
```
