"""

Data files used:
- data/players.tsv 
- data/ratings.tsv 
- data/countries.tsv 
- data/iso3.tsv (
"""

import pandas as pd
import json
import os
from pathlib import Path
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class FIDEDataProcessor:
    def __init__(self, data_dir='./data'):
        
        self.data_dir = data_dir
        self.players_df = None
        self.ratings_df = None
        self.countries_df = None
        self.iso3_df = None
        self.all_data = []
        self.countries_list = []
        self.years = set()
        
    def load_tsv_files(self):
        
        files_to_load = {
            'players.tsv': 'players_df',
            'ratings.tsv': 'ratings_df',
            'countries.tsv': 'countries_df',
            'iso3.tsv': 'iso3_df'
        }
        
        print("Loading FIDE data files...")
        
        for filename, attr_name in files_to_load.items():
            filepath = os.path.join(self.data_dir, filename)
            
            if not os.path.exists(filepath):
                print(f"   {filename} - NOT FOUND")
                return False
            
            try:
                # Read TSV with proper settings
                df = pd.read_csv(
                    filepath, 
                    sep='\t',
                    encoding='utf-8'
                )
                
                # Clean column names
                df.columns = df.columns.str.replace('^#', '', regex=True).str.strip()
                
                
                if 'id' in df.columns:
                    df['id'] = df['id'].astype(str).str.strip()
                
                # Display loaded info
                setattr(self, attr_name, df)
                print(f"   {filename} ({len(df):,} rows) | Columns: {list(df.columns)}")
                
            except Exception as e:
                print(f"   {filename} - ERROR: {e}")
                return False
        
        return True
    
    def create_country_mapping(self):
        #Create mapping from federation code to country name and region
        self.country_map = {}
        
        if self.countries_df is not None:
            for idx, row in self.countries_df.iterrows():
                try:
                    # In countries.tsv: columns are #country, ioc, alpha3
                    fed_code = str(row.get('ioc', '')).strip().upper()
                    country_name = str(row.get('country', 'Unknown')).strip()
                    alpha3 = str(row.get('alpha3', '')).strip()
                    
                    if fed_code:
                        self.country_map[fed_code] = {
                            'name': country_name,
                            'code': fed_code,
                            'alpha3': alpha3,
                            'region': 'Unknown',
                            'subregion': 'Unknown'
                        }
                except:
                    continue
        
        
        if self.iso3_df is not None:
            for idx, row in self.iso3_df.iterrows():
                try:
                    alpha3 = str(row.get('alpha3', '')).strip()
                    region = str(row.get('region', '')).strip()
                    subregion = str(row.get('subregion', '')).strip()
                    
                    
                    for code, info in self.country_map.items():
                        if info['alpha3'] == alpha3:
                            info['region'] = region
                            info['subregion'] = subregion
                except:
                    continue
    
    def process_data(self, use_medium=False):
       
        suffix = '-medium' if use_medium else ''
        
        print(f"\nProcessing data (using {'medium' if use_medium else 'full'} dataset)...")
        
       
        if 'id' not in self.players_df.columns:
            print(f"ERROR: 'id' not found in players.tsv. Available columns: {list(self.players_df.columns)}")
            return False
        
        if 'id' not in self.ratings_df.columns:
            print(f"ERROR: 'id' not found in ratings.tsv. Available columns: {list(self.ratings_df.columns)}")
            return False
        
        print(f"  Merging players with ratings...")
        
        
        merged_df = pd.merge(
            self.players_df,
            self.ratings_df,
            on='id',
            how='inner'
        )
        
        print(f"  Merged records: {len(merged_df):,}")
        
       
        self.create_country_mapping()
        
       
        processed_count = 0
        for idx, row in merged_df.iterrows():
            try:
                player_id = str(row['id'])
                rating = float(row['rating'])
                
               
                month_str = row.get('month_y')  
                if pd.isna(month_str):
                    month_str = row.get('month')
                
                if pd.isna(month_str):
                    continue
                
                month_str = str(month_str).strip()
                
               
                try:
                    month_date = pd.to_datetime(month_str, format='%Y-%m')
                    year = int(month_date.year)
                except:
                    continue
                
                if rating < 400:
                    continue
                
                
                fed_code = str(row.get('fed', '')).strip().upper()
                country_info = self.country_map.get(fed_code, {
                    'name': fed_code,
                    'code': fed_code,
                    'region': 'Unknown',
                    'subregion': 'Unknown',
                    'alpha3': ''
                })
                
                gender = str(row.get('sex', '')).strip().upper()
                if gender not in ['M', 'F']:
                    gender = 'U'
                
                birth_year = row.get('birthyear')
                try:
                    birth_year = int(birth_year) if pd.notna(birth_year) else None
                except:
                    birth_year = None
                
                player_name = str(row.get('name', f'Player_{player_id}'))[:50]
                
                
                age = year - birth_year if birth_year else None
                
                games = row.get('games', 0)
                try:
                    games = int(games) if pd.notna(games) else 0
                except:
                    games = 0
                
                record = {
                    'player_id': player_id,
                    'year': year,
                    'month': month_str,
                    'rating': int(rating),
                    'games': games,
                    'country': country_info['name'],
                    'country_code': country_info['code'],
                    'region': country_info.get('region', 'Unknown'),
                    'subregion': country_info.get('subregion', 'Unknown'),
                    'gender': gender,
                    'birth_year': birth_year,
                    'age': age,
                    'name': player_name
                }
                
                self.all_data.append(record)
                self.years.add(year)
                processed_count += 1
                
                if country_info['name'] not in self.countries_list:
                    self.countries_list.append(country_info['name'])
                
            except Exception as e:
                continue
        
        self.countries_list = sorted(self.countries_list)
        print(f"  Processed records: {len(self.all_data):,}")
        print(f"  Countries found: {len(self.countries_list)}")
        print(f"  Year range: {min(self.years)} - {max(self.years)}" if self.years else "  No years found")
        
        return True
    
    def filter_by_year_range(self, start_year=2010, end_year=None):
        #Filter data to a specific year range
        if end_year is None:
            end_year = max(self.years) if self.years else 2024
        
        original_count = len(self.all_data)
        self.all_data = [d for d in self.all_data if start_year <= d['year'] <= end_year]
        self.years = {y for y in self.years if start_year <= y <= end_year}
        
        print(f"\nFiltered to years {start_year}-{end_year}: {len(self.all_data):,} records (removed {original_count - len(self.all_data):,})")
    
    def filter_top_countries(self, n=20):
        #Keep only top N countries by player count
        country_counts = {}
        for record in self.all_data:
            country = record['country']
            country_counts[country] = country_counts.get(country, 0) + 1
        
        top_countries = sorted(country_counts.items(), key=lambda x: x[1], reverse=True)[:n]
        top_country_names = {c[0] for c in top_countries}
        
        original_count = len(self.all_data)
        self.all_data = [d for d in self.all_data if d['country'] in top_country_names]
        self.countries_list = sorted(list(top_country_names))
        
        print(f"\nFiltered to top {n} countries: {len(self.all_data):,} records (removed {original_count - len(self.all_data):,})")
        print(f"  Countries: {', '.join(self.countries_list[:10])}...")
    
    def sample_by_rating(self, min_rating=1000):
        #Keep only players with max rating >= min_rating
        player_max_ratings = {}
        
        for record in self.all_data:
            pid = record['player_id']
            rating = record['rating']
            if pid not in player_max_ratings:
                player_max_ratings[pid] = rating
            else:
                player_max_ratings[pid] = max(player_max_ratings[pid], rating)
        
        original_count = len(self.all_data)
        self.all_data = [d for d in self.all_data if player_max_ratings[d['player_id']] >= min_rating]
        
        print(f"\nFiltered to players with max rating >= {min_rating}: {len(self.all_data):,} records (removed {original_count - len(self.all_data):,})")
    
    def validate_data(self):
        
        print("\n" + "="*60)
        print("DATA VALIDATION & STATISTICS")
        print("="*60)
        print(f"  Total records: {len(self.all_data):,}")
        print(f"  Unique players: {len(set(d['player_id'] for d in self.all_data)):,}")
        print(f"  Years range: {min(self.years)} - {max(self.years)}" if self.years else "  No years found")
        print(f"  Countries: {len(self.countries_list)}")
        
       
        genders = {}
        for record in self.all_data:
            g = record['gender']
            genders[g] = genders.get(g, 0) + 1
        print(f"\n  Gender distribution:")
        for g in ['M', 'F', 'U']:
            count = genders.get(g, 0)
            pct = (count / len(self.all_data) * 100) if self.all_data else 0
            print(f"    {g}: {count:,} ({pct:.1f}%)")
        
      
        ratings = [d['rating'] for d in self.all_data]
        print(f"\n  Rating statistics:")
        print(f"    Min: {min(ratings)}")
        print(f"    Max: {max(ratings)}")
        print(f"    Mean: {sum(ratings) / len(ratings):.0f}")
        print(f"    Median: {sorted(ratings)[len(ratings)//2]}")
        
        # Top 10 countries
        country_counts = {}
        for record in self.all_data:
            country = record['country']
            country_counts[country] = country_counts.get(country, 0) + 1
        
        print(f"\n  Top 10 countries by record count:")
        for country, count in sorted(country_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"    {country}: {count:,}")
    
    def export_to_json(self, output_file='chess_data.json'):
       
        output_data = {
            'metadata': {
                'generated': datetime.now().isoformat(),
                'total_records': len(self.all_data),
                'unique_players': len(set(d['player_id'] for d in self.all_data)),
                'year_range': {
                    'min': int(min(self.years)) if self.years else None,
                    'max': int(max(self.years)) if self.years else None
                },
                'countries': self.countries_list,
                'gender_values': ['M', 'F', 'U']
            },
            'data': self.all_data
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        file_size = os.path.getsize(output_file) / (1024 * 1024)
        print(f"\n✓ Exported to {output_file} ({file_size:.2f} MB)")
        
        return output_file
    
    def export_aggregated_json(self, output_file='chess_data_aggregated.json'):
        
        aggregated_data = {}
        
        # Group by year and country
        for record in self.all_data:
            year = record['year']
            country = record['country']
            gender = record['gender']
            rating = record['rating']
            
            key = f"{year}_{country}_{gender}"
            
            if key not in aggregated_data:
                aggregated_data[key] = {
                    'year': year,
                    'country': country,
                    'gender': gender,
                    'ratings': [],
                    'count': 0
                }
            
            aggregated_data[key]['ratings'].append(rating)
            aggregated_data[key]['count'] += 1
        
        # Calculate statistics for each group
        aggregated_list = []
        for key, group in aggregated_data.items():
            ratings = group['ratings']
            aggregated_list.append({
                'year': group['year'],
                'country': group['country'],
                'gender': group['gender'],
                'count': group['count'],
                'mean_rating': sum(ratings) / len(ratings),
                'median_rating': sorted(ratings)[len(ratings)//2],
                'min_rating': min(ratings),
                'max_rating': max(ratings)
            })
        
        output_data = {
            'metadata': {
                'generated': datetime.now().isoformat(),
                'total_records': len(self.all_data),
                'aggregated_groups': len(aggregated_list),
                'year_range': {
                    'min': int(min(self.years)) if self.years else None,
                    'max': int(max(self.years)) if self.years else None
                },
                'countries': self.countries_list,
                'gender_values': ['M', 'F', 'U']
            },
            'data': aggregated_list
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        file_size = os.path.getsize(output_file) / (1024 * 1024)
        print(f"✓ Exported aggregated data to {output_file} ({file_size:.2f} MB)")
        
        return output_file


def main():
    
    
    print("="*60)
    print("FIDE CHESS DATA PROCESSOR")
    print("="*60 + "\n")
    
   
    processor = FIDEDataProcessor(data_dir='./data')
    
   
    if not processor.load_tsv_files():
        print("Failed to load data files. Exiting.")
        return
    
   
    if not processor.process_data(use_medium=False):
        print("Failed to process data. Exiting.")
        return
    
   
    processor.filter_by_year_range(start_year=2010)  # Filter to years 2010+
    processor.filter_top_countries(n=30)  # Keep top 30 countries
    
    processor.validate_data()
    
    processor.export_to_json('chess_data.json')
    processor.export_aggregated_json('chess_data_aggregated.json')
    
    print("\n" + "="*60)
    print("Processing complete!")
    print("="*60)


if __name__ == '__main__':
    main()