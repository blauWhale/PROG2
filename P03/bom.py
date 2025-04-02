from bom_service import BOMService
import json

def main():
    service = BOMService()
    
    print("BOM-Daten werden abgerufen...")
    bom_data = service.get_data()
    
    if bom_data:
        print("\nErhaltene Daten:")
        print(json.dumps(bom_data, indent=2))
        
        print("\nFormatierte BOM-Tabelle:")
        table = service.format_bom_table(bom_data)
        print(table)
    else:
        print("Keine Daten erhalten.")

if __name__ == "__main__":
    main()