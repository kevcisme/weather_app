"""
Weather Data Reader Utility

A utility class for reading weather data from S3 using AWS Wrangler.
Designed for use in Jupyter notebooks for ML model development.
"""

import json
import awswrangler as wr
import pandas as pd
from datetime import datetime, timedelta, timezone
from typing import Optional, List


class WeatherDataReader:
    """
    Helper class to read weather data from S3 using AWS Wrangler.
    
    The data is organized in S3 as:
    - Bronze layer (raw): s3://bucket/samples/YYYY-MM-DD/YYYY-MM-DDTHH-MM-SSZ.json
    - Silver layer (enriched): s3://bucket/silver/YYYY-MM-DD/YYYY-MM-DDTHH-MM-SSZ.json
    
    Example:
        >>> reader = WeatherDataReader(
        ...     bucket="my-weather-bucket",
        ...     bronze_prefix="samples",
        ...     silver_prefix="silver"
        ... )
        >>> # Get last 24 hours of enriched data
        >>> df = reader.get_readings(hours=24, layer="silver")
        >>> # Get specific date range
        >>> df = reader.get_readings_by_date_range(
        ...     start_date="2025-10-01",
        ...     end_date="2025-10-07",
        ...     layer="bronze"
        ... )
    """
    
    def __init__(
        self,
        bucket: str,
        bronze_prefix: str = "samples",
        silver_prefix: str = "silver",
        region: str = "us-west-2"
    ):
        """
        Initialize the WeatherDataReader.
        
        Args:
            bucket: S3 bucket name
            bronze_prefix: Prefix for raw data (default: "samples")
            silver_prefix: Prefix for enriched data (default: "silver")
            region: AWS region (default: "us-west-2")
        """
        self.bucket = bucket
        self.bronze_prefix = bronze_prefix.rstrip("/")
        self.silver_prefix = silver_prefix.rstrip("/")
        self.region = region
    
    def _get_s3_paths_for_dates(
        self,
        dates: List[str],
        layer: str = "silver"
    ) -> List[str]:
        """
        Generate S3 paths for a list of dates.
        
        Args:
            dates: List of date strings in YYYY-MM-DD format
            layer: "bronze" or "silver" (default: "silver")
            
        Returns:
            List of S3 paths to scan
        """
        prefix = self.silver_prefix if layer == "silver" else self.bronze_prefix
        paths = []
        
        for date in dates:
            path = f"s3://{self.bucket}/{prefix}/{date}/"
            paths.append(path)
        
        return paths

    def _read_single_json_file(self, json_file_path: str) -> pd.DataFrame:
        """
        Read a single JSON file with robust error handling.

        Args:
            json_file_path: Full S3 path to the JSON file

        Returns:
            DataFrame with the JSON data, or empty DataFrame if reading fails
        """
        try:
            # Parse the S3 path to extract bucket and key
            # Format: s3://bucket/key/path/to/file.json
            path_parts = json_file_path.replace("s3://", "").split("/", 1)
            bucket = path_parts[0]
            key = path_parts[1]

            # Use boto3 directly for more reliable reading
            import boto3
            s3_client = boto3.client('s3')
            
            # Get the object from S3
            response = s3_client.get_object(Bucket=bucket, Key=key)
            file_content = response['Body'].read().decode('utf-8')

            # Parse the JSON
            parsed_json = json.loads(file_content)

            # Handle different JSON structures
            if isinstance(parsed_json, dict):
                # Single JSON object - convert to single-row DataFrame
                return pd.DataFrame([parsed_json])
            elif isinstance(parsed_json, list):
                # List of JSON objects - convert directly
                if len(parsed_json) > 0 and isinstance(parsed_json[0], dict):
                    return pd.DataFrame(parsed_json)
                else:
                    # List of scalar values - skip
                    return pd.DataFrame()
            else:
                # Scalar value - skip
                return pd.DataFrame()

        except json.JSONDecodeError as e:
            print(f"Note: {json_file_path} is not valid JSON: {e}")
            return pd.DataFrame()
        except Exception as e:
            print(f"Note: Could not read {json_file_path}: {e}")
            return pd.DataFrame()

    def get_readings(
        self,
        hours: int = 24,
        layer: str = "silver"
    ) -> pd.DataFrame:
        """
        Get weather readings from the last N hours.
        
        Args:
            hours: Number of hours to look back (default: 24)
            layer: "bronze" or "silver" (default: "silver")
            
        Returns:
            DataFrame with weather readings sorted by timestamp
        """
        now = datetime.now(timezone.utc)
        cutoff_time = now - timedelta(hours=hours)
        
        # Generate dates to check
        dates = []
        current = cutoff_time
        while current <= now:
            date_str = current.strftime("%Y-%m-%d")
            if date_str not in dates:
                dates.append(date_str)
            current += timedelta(days=1)
        
        return self.get_readings_by_dates(dates, layer, cutoff_time)
    
    def get_readings_by_dates(
        self,
        dates: List[str],
        layer: str = "silver",
        cutoff_time: Optional[datetime] = None
    ) -> pd.DataFrame:
        """
        Get weather readings for specific dates.

        Args:
            dates: List of date strings in YYYY-MM-DD format
            layer: "bronze" or "silver" (default: "silver")
            cutoff_time: Optional datetime to filter readings after this time

        Returns:
            DataFrame with weather readings sorted by timestamp
        """
        prefix = self.silver_prefix if layer == "silver" else self.bronze_prefix
        all_data = []

        for date in dates:
            try:
                # List all JSON files in the date directory
                date_path = f"s3://{self.bucket}/{prefix}/{date}/"
                json_files = wr.s3.list_objects(date_path)

                if not json_files:
                    print(f"Note: No files found in {date_path}")
                    continue

                # Filter for .json files only
                json_files = [f for f in json_files if f.endswith('.json')]

                if not json_files:
                    print(f"Note: No JSON files found in {date_path}")
                    continue

                # Read all JSON files for this date
                for json_file in json_files:
                    try:
                        # Try to read the JSON file with different approaches
                        df = self._read_single_json_file(json_file)

                        if df is not None and not df.empty:
                            all_data.append(df)

                    except Exception as e:
                        print(f"Note: Could not read {json_file}: {e}")
                        continue

            except Exception as e:
                print(f"Note: Could not list files for date {date}: {e}")
                continue

        if not all_data:
            return pd.DataFrame()

        # Combine all dataframes
        combined_df = pd.concat(all_data, ignore_index=True)

        # Convert timestamp to datetime
        combined_df['timestamp'] = pd.to_datetime(
            combined_df['ts'],
            format='ISO8601',
            utc=True
        )

        # Filter by cutoff time if provided
        if cutoff_time:
            combined_df = combined_df[combined_df['timestamp'] >= cutoff_time]

        # Sort by timestamp
        combined_df = combined_df.sort_values('timestamp').reset_index(drop=True)

        return combined_df
    
    def get_readings_by_date_range(
        self,
        start_date: str,
        end_date: str,
        layer: str = "silver"
    ) -> pd.DataFrame:
        """
        Get weather readings for a specific date range.
        
        Args:
            start_date: Start date in YYYY-MM-DD format (inclusive)
            end_date: End date in YYYY-MM-DD format (inclusive)
            layer: "bronze" or "silver" (default: "silver")
            
        Returns:
            DataFrame with weather readings sorted by timestamp
        """
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        
        dates = []
        current = start
        while current <= end:
            dates.append(current.strftime("%Y-%m-%d"))
            current += timedelta(days=1)
        
        return self.get_readings_by_dates(dates, layer)
    
    def get_latest_reading(self, layer: str = "silver") -> Optional[dict]:
        """
        Get the most recent weather reading.
        
        Args:
            layer: "bronze" or "silver" (default: "silver")
            
        Returns:
            Dictionary with the latest reading, or None if no data found
        """
        df = self.get_readings(hours=48, layer=layer)
        
        if df.empty:
            return None
        
        # Get the row with the latest timestamp
        latest_row = df.loc[df['timestamp'].idxmax()]
        
        return latest_row.to_dict()
    
    def get_daily_aggregates(
        self,
        start_date: str,
        end_date: str,
        layer: str = "silver"
    ) -> pd.DataFrame:
        """
        Get daily aggregated statistics for a date range.
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            layer: "bronze" or "silver" (default: "silver")
            
        Returns:
            DataFrame with daily min/max/mean/std statistics
        """
        df = self.get_readings_by_date_range(start_date, end_date, layer)
        
        if df.empty:
            return pd.DataFrame()
        
        # Extract date from timestamp
        df['date'] = df['timestamp'].dt.date
        
        # Identify numeric columns for aggregation
        numeric_cols = df.select_dtypes(include=['number']).columns
        
        # Group by date and calculate statistics
        daily_stats = df.groupby('date')[numeric_cols].agg(['min', 'max', 'mean', 'std'])
        
        return daily_stats.reset_index()
    
    def list_available_dates(self, layer: str = "silver") -> List[str]:
        """
        List all available dates with data in the specified layer.

        Args:
            layer: "bronze" or "silver" (default: "silver")

        Returns:
            List of date strings in YYYY-MM-DD format
        """
        prefix = self.silver_prefix if layer == "silver" else self.bronze_prefix
        path = f"s3://{self.bucket}/{prefix}/"

        try:
            # List all objects with the prefix, but limit to avoid too many results
            objects = wr.s3.list_objects(path)

            # Extract unique dates from paths
            dates = set()
            for obj in objects:
                # Extract date from path like: .../YYYY-MM-DD/...
                parts = obj.split('/')
                for part in parts:
                    if len(part) == 10 and part.count('-') == 2:
                        try:
                            datetime.strptime(part, "%Y-%m-%d")
                            dates.add(part)
                        except ValueError:
                            continue

            return sorted(list(dates))

        except Exception as e:
            print(f"Error listing dates: {e}")
            return []

