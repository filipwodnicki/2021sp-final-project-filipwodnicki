{
 "cells": [
  {
   "cell_type": "markdown",
   "id": "43ca5cd2-da7c-4786-9a26-14f3769e1b99",
   "metadata": {},
   "source": [
    "# Transit + OSMnx demo for Kraków"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "1aad5882-0986-4020-b1e5-bbecb4332887",
   "metadata": {},
   "source": [
    "The purpose of this notebook is to compare the transit schedule in Kraków on Sep 30, 2021 with Sep 30, 2019- prepandemic.\n",
    "\n",
    "Approach:\n",
    "- We'll focus on trams\n",
    "- Visualization is important\n",
    "- Static map is fine, sharing is great\n",
    "\n",
    "Data:\n",
    "- GTFS schedules, via API call ideally, can be CSV  \n",
    "\n",
    "Schedule: [3 Sep 2019](https://transitfeeds.com/p/mpk-sa-w-krakowie/1105/20190903), [2 Sep 2020](https://transitfeeds.com/p/mpk-sa-w-krakowie/1105/20200902), [1 Sep 2021](https://transitfeeds.com/p/mpk-sa-w-krakowie/1105/20210901-10)\n",
    "\n",
    "Methodology:\n",

    "1. Load GTFS data ✅\n",
    "2. Process using Transit + OSMnx ✅   \n",
    "(3. Test and refactor code as needed.) \n",
    "4. Visualize schedule 🔁\n",
    "5. Compare schedules\n",
    "6. Share\n",
    "----\n",
    "7. Experiment with summary statistics\n",
    "\n",
    "Assumptions\n",
    "- Data on \"relations\" is out of scope"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "7fe25012-5b54-468a-b4ba-239c58779ef5",
   "metadata": {},
   "source": [
    "## Setup"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 283,
   "id": "72cc5fd1-776a-4223-8e76-5dba1702198b",
   "metadata": {},
   "outputs": [
    {
     "ename": "ModuleNotFoundError",
     "evalue": "No module named 'mpl_toolkits.basemap'",
     "output_type": "error",
     "traceback": [
      "\u001b[0;31m---------------------------------------------------------------------------\u001b[0m",
      "\u001b[0;31mModuleNotFoundError\u001b[0m                       Traceback (most recent call last)",
      "\u001b[0;32m/var/folders/lh/lxn1p44d76z_4wqtzp5jpccr0000gn/T/ipykernel_9562/4031614008.py\u001b[0m in \u001b[0;36m<module>\u001b[0;34m\u001b[0m\n\u001b[1;32m      1\u001b[0m \u001b[0;32mimport\u001b[0m \u001b[0mos\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n\u001b[1;32m      2\u001b[0m \u001b[0;32mimport\u001b[0m \u001b[0mmatplotlib\u001b[0m\u001b[0;34m.\u001b[0m\u001b[0mpyplot\u001b[0m \u001b[0;32mas\u001b[0m \u001b[0mplt\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n\u001b[0;32m----> 3\u001b[0;31m \u001b[0;32mfrom\u001b[0m \u001b[0mmpl_toolkits\u001b[0m\u001b[0;34m.\u001b[0m\u001b[0mbasemap\u001b[0m \u001b[0;32mimport\u001b[0m \u001b[0mBasemap\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n\u001b[0m\u001b[1;32m      4\u001b[0m \u001b[0;32mimport\u001b[0m \u001b[0mpandas\u001b[0m \u001b[0;32mas\u001b[0m \u001b[0mpd\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n\u001b[1;32m      5\u001b[0m \u001b[0;32mimport\u001b[0m \u001b[0mgeopandas\u001b[0m \u001b[0;32mas\u001b[0m \u001b[0mgpd\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n",
      "\u001b[0;31mModuleNotFoundError\u001b[0m: No module named 'mpl_toolkits.basemap'"
     ]
    }
   ],
   "source": [
    "import os\n",
    "import matplotlib.pyplot as plt\n",
    "from mpl_toolkits.basemap import Basemap\n",
    "import pandas as pd\n",
    "import geopandas as gpd\n",
    "import partridge as ptg"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 2,
   "id": "36144bd4-f7c2-4d78-9437-48b948cf85d1",
   "metadata": {},
   "outputs": [],
   "source": [
    "os.chdir(os.path.dirname(os.getcwd()))"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 3,
   "id": "b0c94074-c315-4bfc-a71d-5f8b1417cf71",
   "metadata": {},
   "outputs": [],
   "source": [
    "from final_project.network import WalkNetwork, TransitNetwork, MultiNetwork"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 4,
   "id": "5d55fc9d-b6d9-42b2-987e-e05316030e9f",
   "metadata": {},
   "outputs": [],
   "source": [
    "data_2019 = os.path.join(\"demo\", \"data\", \"krakow_tram_20190903.zip\")\n",
    "data_2020 = os.path.join(\"demo\", \"data\", \"krakow_tram_20200902.zip\")\n",
    "data_2021 = os.path.join(\"demo\", \"data\", \"krakow_tram_20210901.zip\")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 5,
   "id": "730116bc-8dd3-486f-9461-6636aa145806",
   "metadata": {},
   "outputs": [],
   "source": [
    "pd.set_option('display.max_rows', 1000)\n",
    "pd.set_option('display.max_columns', 100)"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "5b5e67f9-8043-4ee7-919d-2391eaea8afb",
   "metadata": {},
   "source": [
    "## Load data with \"Transit + OSMnx\""
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 218,
   "id": "7a1648e3-e26e-4deb-ae8a-aaa8d7767b1f",
   "metadata": {},
   "outputs": [],
   "source": [
    "T = TransitNetwork.create_from_gtfs(data_2021)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 219,
   "id": "13a9b1ea-6652-4aa6-8699-29a8022a56e5",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "{'boarding_cost': 400.0, 'modes': ['900'], 'y': 50.06473, 'x': 20.08479}"
      ]
     },
     "execution_count": 219,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "pd.DataFrame(T.nodes.data()).iloc[3][1]"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 220,
   "id": "cd6fb7ab-4924-4b48-a20e-e3966dda55e7",
   "metadata": {},
   "outputs": [],
   "source": [
    "# T.mapper"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "ab67cec3-c8b0-41fd-919a-902d84915144",
   "metadata": {},
   "source": [
    "# Partridge"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "4a67c815-c304-4bb8-8413-6d43645dc277",
   "metadata": {},
   "source": [
    "## Library overview"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 221,
   "id": "c29fff11-0621-4247-84a4-b6472d99a870",
   "metadata": {},
   "outputs": [],
   "source": [
    "# Get date, service_ids\n",
    "date, service_ids = ptg.read_busiest_date(data_2021)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 222,
   "id": "7a75acb9-5334-4d01-ac74-28f622a7955b",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "2021-09-03\n"
     ]
    }
   ],
   "source": [
    "print(date)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 223,
   "id": "2fbb9a7c-6749-47e5-addf-685488f01f38",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "frozenset({'service_4'})\n"
     ]
    }
   ],
   "source": [
    "print(service_ids)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 246,
   "id": "1bfc7e82-1ee3-4331-a6f4-be941785e914",
   "metadata": {},
   "outputs": [],
   "source": [
    "# Load feed\n",
    "view = {\n",
    "    'trips.txt': {'service_id': service_ids},\n",
    "}\n",
    "\n",
    "feed = ptg.load_feed(data_2021, view)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 247,
   "id": "67f1e459-c261-430b-a687-9e0d5262d4a9",
   "metadata": {},
   "outputs": [],
   "source": [
    "# Load geofeed\n",
    "feed = ptg.load_geo_feed(data_2021, view)"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "37bae1be-6f9f-476a-884d-5bb67c8eca04",
   "metadata": {},
   "source": [
    "**Interpretation:** We can look at:"
   ]
  },
  {
   "cell_type": "raw",
   "id": "8b8e6228-00e2-4d92-9098-654fe08daf8c",
   "metadata": {},
   "source": [
    "feed.agency\n",
    "feed.calendar\n",
    "feed.calendar_dates\n",
    "feed.fare_attributes\n",
    "feed.fare_rules\n",
    "feed.feed_info\n",
    "feed.frequencies\n",
    "feed.routes\n",
    "feed.shapes\n",
    "feed.stop_times\n",
    "feed.stops\n",
    "feed.transfers\n",
    "feed.trips"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 248,
   "id": "799638e7-06e6-45c4-b1ed-1a105e8ff60e",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/html": [
       "<div>\n",
       "<style scoped>\n",
       "    .dataframe tbody tr th:only-of-type {\n",
       "        vertical-align: middle;\n",
       "    }\n",
       "\n",
       "    .dataframe tbody tr th {\n",
       "        vertical-align: top;\n",
       "    }\n",
       "\n",
       "    .dataframe thead th {\n",
       "        text-align: right;\n",
       "    }\n",
       "</style>\n",
       "<table border=\"1\" class=\"dataframe\">\n",
       "  <thead>\n",
       "    <tr style=\"text-align: right;\">\n",
       "      <th></th>\n",
       "      <th>agency_id</th>\n",
       "      <th>agency_name</th>\n",
       "      <th>agency_url</th>\n",
       "      <th>agency_timezone</th>\n",
       "      <th>agency_lang</th>\n",
       "      <th>agency_phone</th>\n",
       "      <th>agency_fare_url</th>\n",
       "    </tr>\n",
       "  </thead>\n",
       "  <tbody>\n",
       "    <tr>\n",
       "      <th>0</th>\n",
       "      <td>agency_1</td>\n",
       "      <td>ZTP  Kraków</td>\n",
       "      <td>http://ztp.krakow.pl/</td>\n",
       "      <td>Europe/Warsaw</td>\n",
       "      <td>NaN</td>\n",
       "      <td>+48 12 19 150</td>\n",
       "      <td>NaN</td>\n",
       "    </tr>\n",
       "  </tbody>\n",
       "</table>\n",
       "</div>"
      ],
      "text/plain": [
       "  agency_id  agency_name             agency_url agency_timezone agency_lang  \\\n",
       "0  agency_1  ZTP  Kraków  http://ztp.krakow.pl/   Europe/Warsaw         NaN   \n",
       "\n",
       "    agency_phone agency_fare_url  \n",
       "0  +48 12 19 150             NaN  "
      ]
     },
     "execution_count": 248,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "feed.agency"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 249,
   "id": "09697e50-bd1e-479b-9398-53b120dfe5d3",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/html": [
       "<div>\n",
       "<style scoped>\n",
       "    .dataframe tbody tr th:only-of-type {\n",
       "        vertical-align: middle;\n",
       "    }\n",
       "\n",
       "    .dataframe tbody tr th {\n",
       "        vertical-align: top;\n",
       "    }\n",
       "\n",
       "    .dataframe thead th {\n",
       "        text-align: right;\n",
       "    }\n",
       "</style>\n",
       "<table border=\"1\" class=\"dataframe\">\n",
       "  <thead>\n",
       "    <tr style=\"text-align: right;\">\n",
       "      <th></th>\n",
       "      <th>service_id</th>\n",
       "      <th>monday</th>\n",
       "      <th>tuesday</th>\n",
       "      <th>wednesday</th>\n",
       "      <th>thursday</th>\n",
       "      <th>friday</th>\n",
       "      <th>saturday</th>\n",
       "      <th>sunday</th>\n",
       "      <th>start_date</th>\n",
       "      <th>end_date</th>\n",
       "    </tr>\n",
       "  </thead>\n",
       "  <tbody>\n",
       "    <tr>\n",
       "      <th>0</th>\n",
       "      <td>service_4</td>\n",
       "      <td>0</td>\n",
       "      <td>0</td>\n",
       "      <td>0</td>\n",
       "      <td>0</td>\n",
       "      <td>1</td>\n",
       "      <td>0</td>\n",
       "      <td>0</td>\n",
       "      <td>2021-08-30</td>\n",
       "      <td>2021-11-28</td>\n",
       "    </tr>\n",
       "  </tbody>\n",
       "</table>\n",
       "</div>"
      ],
      "text/plain": [
       "  service_id  monday  tuesday  wednesday  thursday  friday  saturday  sunday  \\\n",
       "0  service_4       0        0          0         0       1         0       0   \n",
       "\n",
       "   start_date    end_date  \n",
       "0  2021-08-30  2021-11-28  "
      ]
     },
     "execution_count": 249,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "feed.calendar"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 250,
   "id": "caedaf78-a242-4444-8351-77f42a0abed1",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/html": [
       "<div>\n",
       "<style scoped>\n",
       "    .dataframe tbody tr th:only-of-type {\n",
       "        vertical-align: middle;\n",
       "    }\n",
       "\n",
       "    .dataframe tbody tr th {\n",
       "        vertical-align: top;\n",
       "    }\n",
       "\n",
       "    .dataframe thead th {\n",
       "        text-align: right;\n",
       "    }\n",
       "</style>\n",
       "<table border=\"1\" class=\"dataframe\">\n",
       "  <thead>\n",
       "    <tr style=\"text-align: right;\">\n",
       "      <th></th>\n",
       "      <th>service_id</th>\n",
       "      <th>date</th>\n",
       "      <th>exception_type</th>\n",
       "    </tr>\n",
       "  </thead>\n",
       "  <tbody>\n",
       "  </tbody>\n",
       "</table>\n",
       "</div>"
      ],
      "text/plain": [
       "Empty DataFrame\n",
       "Columns: [service_id, date, exception_type]\n",
       "Index: []"
      ]
     },
     "execution_count": 250,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "feed.calendar_dates"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 251,
   "id": "58c6e598-9337-4335-acb1-d09947329f41",
   "metadata": {},
   "outputs": [
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "/Users/filip/code/anaconda3/envs/rs/lib/python3.9/site-packages/pyproj/crs/crs.py:131: FutureWarning: '+init=<authority>:<code>' syntax is deprecated. '<authority>:<code>' is the preferred initialization method. When making the change, be mindful of axis order changes: https://pyproj4.github.io/pyproj/stable/gotchas.html#axis-order-changes-in-proj-6\n",
      "  in_crs_string = _prepare_from_proj_string(in_crs_string)\n"
     ]
    },
    {
     "data": {
      "text/html": [
       "<div>\n",
       "<style scoped>\n",
       "    .dataframe tbody tr th:only-of-type {\n",
       "        vertical-align: middle;\n",
       "    }\n",
       "\n",
       "    .dataframe tbody tr th {\n",
       "        vertical-align: top;\n",
       "    }\n",
       "\n",
       "    .dataframe thead th {\n",
       "        text-align: right;\n",
       "    }\n",
       "</style>\n",
       "<table border=\"1\" class=\"dataframe\">\n",
       "  <thead>\n",
       "    <tr style=\"text-align: right;\">\n",
       "      <th></th>\n",
       "      <th>fare_id</th>\n",
       "      <th>price</th>\n",
       "      <th>currency_type</th>\n",
       "      <th>payment_method</th>\n",
       "      <th>transfers</th>\n",
       "    </tr>\n",
       "  </thead>\n",
       "  <tbody>\n",
       "  </tbody>\n",
       "</table>\n",
       "</div>"
      ],
      "text/plain": [
       "Empty DataFrame\n",
       "Columns: [fare_id, price, currency_type, payment_method, transfers]\n",
       "Index: []"
      ]
     },
     "execution_count": 251,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "feed.fare_attributes"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 252,
   "id": "4afe7b7a-2a4c-4e55-87d4-9d1091c18146",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/html": [
       "<div>\n",
       "<style scoped>\n",
       "    .dataframe tbody tr th:only-of-type {\n",
       "        vertical-align: middle;\n",
       "    }\n",
       "\n",
       "    .dataframe tbody tr th {\n",
       "        vertical-align: top;\n",
       "    }\n",
       "\n",
       "    .dataframe thead th {\n",
       "        text-align: right;\n",
       "    }\n",
       "</style>\n",
       "<table border=\"1\" class=\"dataframe\">\n",
       "  <thead>\n",
       "    <tr style=\"text-align: right;\">\n",
       "      <th></th>\n",
       "      <th>fare_id</th>\n",
       "    </tr>\n",
       "  </thead>\n",
       "  <tbody>\n",
       "  </tbody>\n",
       "</table>\n",
       "</div>"
      ],
      "text/plain": [
       "Empty DataFrame\n",
       "Columns: [fare_id]\n",
       "Index: []"
      ]
     },
     "execution_count": 252,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "feed.fare_rules"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 253,
   "id": "d6ee1983-f6f5-4f2e-9441-76bcb9de5069",
   "metadata": {},
   "outputs": [],
   "source": [
    "# feed.feed_info  # errors out"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 254,
   "id": "f9a59e06-adfb-4393-a694-75a5e06a389c",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/html": [
       "<div>\n",
       "<style scoped>\n",
       "    .dataframe tbody tr th:only-of-type {\n",
       "        vertical-align: middle;\n",
       "    }\n",
       "\n",
       "    .dataframe tbody tr th {\n",
       "        vertical-align: top;\n",
       "    }\n",
       "\n",
       "    .dataframe thead th {\n",
       "        text-align: right;\n",
       "    }\n",
       "</style>\n",
       "<table border=\"1\" class=\"dataframe\">\n",
       "  <thead>\n",
       "    <tr style=\"text-align: right;\">\n",
       "      <th></th>\n",
       "      <th>trip_id</th>\n",
       "      <th>start_time</th>\n",
       "      <th>end_time</th>\n",
       "      <th>headway_secs</th>\n",
       "    </tr>\n",
       "  </thead>\n",
       "  <tbody>\n",
       "  </tbody>\n",
       "</table>\n",
       "</div>"
      ],
      "text/plain": [
       "Empty DataFrame\n",
       "Columns: [trip_id, start_time, end_time, headway_secs]\n",
       "Index: []"
      ]
     },
     "execution_count": 254,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "feed.frequencies\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 255,
   "id": "2ede075e-ec69-451b-99e6-e53cafef0cff",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/html": [
       "<div>\n",
       "<style scoped>\n",
       "    .dataframe tbody tr th:only-of-type {\n",
       "        vertical-align: middle;\n",
       "    }\n",
       "\n",
       "    .dataframe tbody tr th {\n",
       "        vertical-align: top;\n",
       "    }\n",
       "\n",
       "    .dataframe thead th {\n",
       "        text-align: right;\n",
       "    }\n",
       "</style>\n",
       "<table border=\"1\" class=\"dataframe\">\n",
       "  <thead>\n",
       "    <tr style=\"text-align: right;\">\n",
       "      <th></th>\n",
       "      <th>route_id</th>\n",
       "      <th>agency_id</th>\n",
       "      <th>route_short_name</th>\n",
       "      <th>route_long_name</th>\n",
       "      <th>route_desc</th>\n",
       "      <th>route_type</th>\n",
       "      <th>route_url</th>\n",
       "      <th>route_color</th>\n",
       "      <th>route_text_color</th>\n",
       "    </tr>\n",
       "  </thead>\n",
       "  <tbody>\n",
       "    <tr>\n",
       "      <th>0</th>\n",
       "      <td>route_31</td>\n",
       "      <td>agency_1</td>\n",
       "      <td>1</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>900</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>1</th>\n",
       "      <td>route_43</td>\n",
       "      <td>agency_1</td>\n",
       "      <td>19</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>900</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>2</th>\n",
       "      <td>route_46</td>\n",
       "      <td>agency_1</td>\n",
       "      <td>22</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>900</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>3</th>\n",
       "      <td>route_53</td>\n",
       "      <td>agency_1</td>\n",
       "      <td>62</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>900</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>4</th>\n",
       "      <td>route_54</td>\n",
       "      <td>agency_1</td>\n",
       "      <td>64</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>900</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>5</th>\n",
       "      <td>route_55</td>\n",
       "      <td>agency_1</td>\n",
       "      <td>3</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>900</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>6</th>\n",
       "      <td>route_56</td>\n",
       "      <td>agency_1</td>\n",
       "      <td>69</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>900</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>7</th>\n",
       "      <td>route_58</td>\n",
       "      <td>agency_1</td>\n",
       "      <td>9</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>900</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>8</th>\n",
       "      <td>route_59</td>\n",
       "      <td>agency_1</td>\n",
       "      <td>11</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>900</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>9</th>\n",
       "      <td>route_62</td>\n",
       "      <td>agency_1</td>\n",
       "      <td>24</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>900</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>10</th>\n",
       "      <td>route_63</td>\n",
       "      <td>agency_1</td>\n",
       "      <td>50</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>900</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>11</th>\n",
       "      <td>route_69</td>\n",
       "      <td>agency_1</td>\n",
       "      <td>18</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>900</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>12</th>\n",
       "      <td>route_70</td>\n",
       "      <td>agency_1</td>\n",
       "      <td>52</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>900</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>13</th>\n",
       "      <td>route_698</td>\n",
       "      <td>agency_1</td>\n",
       "      <td>21</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>900</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>14</th>\n",
       "      <td>route_806</td>\n",
       "      <td>agency_1</td>\n",
       "      <td>4</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>900</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>15</th>\n",
       "      <td>route_807</td>\n",
       "      <td>agency_1</td>\n",
       "      <td>8</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>900</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>16</th>\n",
       "      <td>route_808</td>\n",
       "      <td>agency_1</td>\n",
       "      <td>13</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>900</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>17</th>\n",
       "      <td>route_809</td>\n",
       "      <td>agency_1</td>\n",
       "      <td>20</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>900</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>18</th>\n",
       "      <td>route_942</td>\n",
       "      <td>agency_1</td>\n",
       "      <td>5</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>900</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>19</th>\n",
       "      <td>route_943</td>\n",
       "      <td>agency_1</td>\n",
       "      <td>14</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>900</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>20</th>\n",
       "      <td>route_944</td>\n",
       "      <td>agency_1</td>\n",
       "      <td>49</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>900</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>21</th>\n",
       "      <td>route_954</td>\n",
       "      <td>agency_1</td>\n",
       "      <td>2</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>900</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>22</th>\n",
       "      <td>route_955</td>\n",
       "      <td>agency_1</td>\n",
       "      <td>6</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>900</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>23</th>\n",
       "      <td>route_956</td>\n",
       "      <td>agency_1</td>\n",
       "      <td>10</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>900</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>24</th>\n",
       "      <td>route_957</td>\n",
       "      <td>agency_1</td>\n",
       "      <td>16</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>900</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "    </tr>\n",
       "  </tbody>\n",
       "</table>\n",
       "</div>"
      ],
      "text/plain": [
       "     route_id agency_id route_short_name route_long_name route_desc  \\\n",
       "0    route_31  agency_1                1             NaN        NaN   \n",
       "1    route_43  agency_1               19             NaN        NaN   \n",
       "2    route_46  agency_1               22             NaN        NaN   \n",
       "3    route_53  agency_1               62             NaN        NaN   \n",
       "4    route_54  agency_1               64             NaN        NaN   \n",
       "5    route_55  agency_1                3             NaN        NaN   \n",
       "6    route_56  agency_1               69             NaN        NaN   \n",
       "7    route_58  agency_1                9             NaN        NaN   \n",
       "8    route_59  agency_1               11             NaN        NaN   \n",
       "9    route_62  agency_1               24             NaN        NaN   \n",
       "10   route_63  agency_1               50             NaN        NaN   \n",
       "11   route_69  agency_1               18             NaN        NaN   \n",
       "12   route_70  agency_1               52             NaN        NaN   \n",
       "13  route_698  agency_1               21             NaN        NaN   \n",
       "14  route_806  agency_1                4             NaN        NaN   \n",
       "15  route_807  agency_1                8             NaN        NaN   \n",
       "16  route_808  agency_1               13             NaN        NaN   \n",
       "17  route_809  agency_1               20             NaN        NaN   \n",
       "18  route_942  agency_1                5             NaN        NaN   \n",
       "19  route_943  agency_1               14             NaN        NaN   \n",
       "20  route_944  agency_1               49             NaN        NaN   \n",
       "21  route_954  agency_1                2             NaN        NaN   \n",
       "22  route_955  agency_1                6             NaN        NaN   \n",
       "23  route_956  agency_1               10             NaN        NaN   \n",
       "24  route_957  agency_1               16             NaN        NaN   \n",
       "\n",
       "    route_type route_url route_color route_text_color  \n",
       "0          900       NaN         NaN              NaN  \n",
       "1          900       NaN         NaN              NaN  \n",
       "2          900       NaN         NaN              NaN  \n",
       "3          900       NaN         NaN              NaN  \n",
       "4          900       NaN         NaN              NaN  \n",
       "5          900       NaN         NaN              NaN  \n",
       "6          900       NaN         NaN              NaN  \n",
       "7          900       NaN         NaN              NaN  \n",
       "8          900       NaN         NaN              NaN  \n",
       "9          900       NaN         NaN              NaN  \n",
       "10         900       NaN         NaN              NaN  \n",
       "11         900       NaN         NaN              NaN  \n",
       "12         900       NaN         NaN              NaN  \n",
       "13         900       NaN         NaN              NaN  \n",
       "14         900       NaN         NaN              NaN  \n",
       "15         900       NaN         NaN              NaN  \n",
       "16         900       NaN         NaN              NaN  \n",
       "17         900       NaN         NaN              NaN  \n",
       "18         900       NaN         NaN              NaN  \n",
       "19         900       NaN         NaN              NaN  \n",
       "20         900       NaN         NaN              NaN  \n",
       "21         900       NaN         NaN              NaN  \n",
       "22         900       NaN         NaN              NaN  \n",
       "23         900       NaN         NaN              NaN  \n",
       "24         900       NaN         NaN              NaN  "
      ]
     },
     "execution_count": 255,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "feed.routes"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 256,
   "id": "01829f61-7cb1-4922-8473-116eaddb8bbb",
   "metadata": {},
   "outputs": [
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "/Users/filip/code/anaconda3/envs/rs/lib/python3.9/site-packages/pyproj/crs/crs.py:131: FutureWarning: '+init=<authority>:<code>' syntax is deprecated. '<authority>:<code>' is the preferred initialization method. When making the change, be mindful of axis order changes: https://pyproj4.github.io/pyproj/stable/gotchas.html#axis-order-changes-in-proj-6\n",
      "  in_crs_string = _prepare_from_proj_string(in_crs_string)\n"
     ]
    },
    {
     "data": {
      "text/html": [
       "<div>\n",
       "<style scoped>\n",
       "    .dataframe tbody tr th:only-of-type {\n",
       "        vertical-align: middle;\n",
       "    }\n",
       "\n",
       "    .dataframe tbody tr th {\n",
       "        vertical-align: top;\n",
       "    }\n",
       "\n",
       "    .dataframe thead th {\n",
       "        text-align: right;\n",
       "    }\n",
       "</style>\n",
       "<table border=\"1\" class=\"dataframe\">\n",
       "  <thead>\n",
       "    <tr style=\"text-align: right;\">\n",
       "      <th></th>\n",
       "      <th>shape_id</th>\n",
       "      <th>geometry</th>\n",
       "    </tr>\n",
       "  </thead>\n",
       "  <tbody>\n",
       "  </tbody>\n",
       "</table>\n",
       "</div>"
      ],
      "text/plain": [
       "Empty GeoDataFrame\n",
       "Columns: [shape_id, geometry]\n",
       "Index: []"
      ]
     },
     "execution_count": 256,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "feed.shapes"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "a8a93b7f-0c50-46ce-9f93-8cc75452f721",
   "metadata": {},
   "source": [
    "**Interpretation:** The Kraków GTFS feed doesn't include geometrycalendar"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 257,
   "id": "4a510888-4e2d-42be-b339-56ab4f16299b",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/html": [
       "<div>\n",
       "<style scoped>\n",
       "    .dataframe tbody tr th:only-of-type {\n",
       "        vertical-align: middle;\n",
       "    }\n",
       "\n",
       "    .dataframe tbody tr th {\n",
       "        vertical-align: top;\n",
       "    }\n",
       "\n",
       "    .dataframe thead th {\n",
       "        text-align: right;\n",
       "    }\n",
       "</style>\n",
       "<table border=\"1\" class=\"dataframe\">\n",
       "  <thead>\n",
       "    <tr style=\"text-align: right;\">\n",
       "      <th></th>\n",
       "      <th>trip_id</th>\n",
       "      <th>arrival_time</th>\n",
       "      <th>departure_time</th>\n",
       "      <th>stop_id</th>\n",
       "      <th>stop_sequence</th>\n",
       "      <th>stop_headsign</th>\n",
       "      <th>pickup_type</th>\n",
       "      <th>drop_off_type</th>\n",
       "      <th>shape_dist_traveled</th>\n",
       "      <th>timepoint</th>\n",
       "    </tr>\n",
       "  </thead>\n",
       "  <tbody>\n",
       "    <tr>\n",
       "      <th>0</th>\n",
       "      <td>block_77_trip_1_service_4</td>\n",
       "      <td>19320.0</td>\n",
       "      <td>19320.0</td>\n",
       "      <td>stop_267_45929</td>\n",
       "      <td>2</td>\n",
       "      <td>NaN</td>\n",
       "      <td>1</td>\n",
       "      <td>0</td>\n",
       "      <td>NaN</td>\n",
       "      <td>1</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>1</th>\n",
       "      <td>block_77_trip_1_service_4</td>\n",
       "      <td>19560.0</td>\n",
       "      <td>19560.0</td>\n",
       "      <td>stop_253_42329</td>\n",
       "      <td>3</td>\n",
       "      <td>NaN</td>\n",
       "      <td>1</td>\n",
       "      <td>0</td>\n",
       "      <td>NaN</td>\n",
       "      <td>1</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>2</th>\n",
       "      <td>block_77_trip_1_service_4</td>\n",
       "      <td>19800.0</td>\n",
       "      <td>19800.0</td>\n",
       "      <td>stop_353_274419</td>\n",
       "      <td>4</td>\n",
       "      <td>NaN</td>\n",
       "      <td>1</td>\n",
       "      <td>0</td>\n",
       "      <td>NaN</td>\n",
       "      <td>1</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>3</th>\n",
       "      <td>block_77_trip_1_service_4</td>\n",
       "      <td>19860.0</td>\n",
       "      <td>19860.0</td>\n",
       "      <td>stop_248_41329</td>\n",
       "      <td>5</td>\n",
       "      <td>NaN</td>\n",
       "      <td>1</td>\n",
       "      <td>0</td>\n",
       "      <td>NaN</td>\n",
       "      <td>1</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>4</th>\n",
       "      <td>block_77_trip_1_service_4</td>\n",
       "      <td>20040.0</td>\n",
       "      <td>20040.0</td>\n",
       "      <td>stop_246_40829</td>\n",
       "      <td>6</td>\n",
       "      <td>NaN</td>\n",
       "      <td>1</td>\n",
       "      <td>0</td>\n",
       "      <td>NaN</td>\n",
       "      <td>1</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>...</th>\n",
       "      <td>...</td>\n",
       "      <td>...</td>\n",
       "      <td>...</td>\n",
       "      <td>...</td>\n",
       "      <td>...</td>\n",
       "      <td>...</td>\n",
       "      <td>...</td>\n",
       "      <td>...</td>\n",
       "      <td>...</td>\n",
       "      <td>...</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>104880</th>\n",
       "      <td>block_720_trip_8_service_4</td>\n",
       "      <td>103920.0</td>\n",
       "      <td>103920.0</td>\n",
       "      <td>stop_248_41319</td>\n",
       "      <td>32</td>\n",
       "      <td>NaN</td>\n",
       "      <td>0</td>\n",
       "      <td>0</td>\n",
       "      <td>NaN</td>\n",
       "      <td>1</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>104881</th>\n",
       "      <td>block_720_trip_8_service_4</td>\n",
       "      <td>104160.0</td>\n",
       "      <td>104160.0</td>\n",
       "      <td>stop_353_274419</td>\n",
       "      <td>33</td>\n",
       "      <td>NaN</td>\n",
       "      <td>1</td>\n",
       "      <td>0</td>\n",
       "      <td>NaN</td>\n",
       "      <td>1</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>104882</th>\n",
       "      <td>block_720_trip_9_service_4</td>\n",
       "      <td>104280.0</td>\n",
       "      <td>104280.0</td>\n",
       "      <td>stop_253_42319</td>\n",
       "      <td>2</td>\n",
       "      <td>NaN</td>\n",
       "      <td>1</td>\n",
       "      <td>0</td>\n",
       "      <td>NaN</td>\n",
       "      <td>1</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>104883</th>\n",
       "      <td>block_720_trip_9_service_4</td>\n",
       "      <td>104460.0</td>\n",
       "      <td>104460.0</td>\n",
       "      <td>stop_267_45919</td>\n",
       "      <td>3</td>\n",
       "      <td>NaN</td>\n",
       "      <td>1</td>\n",
       "      <td>0</td>\n",
       "      <td>NaN</td>\n",
       "      <td>1</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>104884</th>\n",
       "      <td>block_720_trip_9_service_4</td>\n",
       "      <td>104700.0</td>\n",
       "      <td>104700.0</td>\n",
       "      <td>stop_274_46619</td>\n",
       "      <td>4</td>\n",
       "      <td>NaN</td>\n",
       "      <td>1</td>\n",
       "      <td>0</td>\n",
       "      <td>NaN</td>\n",
       "      <td>1</td>\n",
       "    </tr>\n",
       "  </tbody>\n",
       "</table>\n",
       "<p>104885 rows × 10 columns</p>\n",
       "</div>"
      ],
      "text/plain": [
       "                           trip_id  arrival_time  departure_time  \\\n",
       "0        block_77_trip_1_service_4       19320.0         19320.0   \n",
       "1        block_77_trip_1_service_4       19560.0         19560.0   \n",
       "2        block_77_trip_1_service_4       19800.0         19800.0   \n",
       "3        block_77_trip_1_service_4       19860.0         19860.0   \n",
       "4        block_77_trip_1_service_4       20040.0         20040.0   \n",
       "...                            ...           ...             ...   \n",
       "104880  block_720_trip_8_service_4      103920.0        103920.0   \n",
       "104881  block_720_trip_8_service_4      104160.0        104160.0   \n",
       "104882  block_720_trip_9_service_4      104280.0        104280.0   \n",
       "104883  block_720_trip_9_service_4      104460.0        104460.0   \n",
       "104884  block_720_trip_9_service_4      104700.0        104700.0   \n",
       "\n",
       "                stop_id  stop_sequence stop_headsign  pickup_type  \\\n",
       "0        stop_267_45929              2           NaN            1   \n",
       "1        stop_253_42329              3           NaN            1   \n",
       "2       stop_353_274419              4           NaN            1   \n",
       "3        stop_248_41329              5           NaN            1   \n",
       "4        stop_246_40829              6           NaN            1   \n",
       "...                 ...            ...           ...          ...   \n",
       "104880   stop_248_41319             32           NaN            0   \n",
       "104881  stop_353_274419             33           NaN            1   \n",
       "104882   stop_253_42319              2           NaN            1   \n",
       "104883   stop_267_45919              3           NaN            1   \n",
       "104884   stop_274_46619              4           NaN            1   \n",
       "\n",
       "       drop_off_type  shape_dist_traveled  timepoint  \n",
       "0                  0                  NaN          1  \n",
       "1                  0                  NaN          1  \n",
       "2                  0                  NaN          1  \n",
       "3                  0                  NaN          1  \n",
       "4                  0                  NaN          1  \n",
       "...              ...                  ...        ...  \n",
       "104880             0                  NaN          1  \n",
       "104881             0                  NaN          1  \n",
       "104882             0                  NaN          1  \n",
       "104883             0                  NaN          1  \n",
       "104884             0                  NaN          1  \n",
       "\n",
       "[104885 rows x 10 columns]"
      ]
     },
     "execution_count": 257,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "feed.stop_times"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 258,
   "id": "db4f020e-1629-41bf-8584-27bcb3beb48c",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "3.85"
      ]
     },
     "execution_count": 258,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "feed.stop_times.arrival_time.min() / 60 / 60"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 259,
   "id": "70ed7c0a-6081-4b73-9a71-5042f3e944b7",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "29.45"
      ]
     },
     "execution_count": 259,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "feed.stop_times.arrival_time.max() / 60 / 60"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 260,
   "id": "845f5965-9ed9-42e8-8e97-ce05245689e8",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/html": [
       "<div>\n",
       "<style scoped>\n",
       "    .dataframe tbody tr th:only-of-type {\n",
       "        vertical-align: middle;\n",
       "    }\n",
       "\n",
       "    .dataframe tbody tr th {\n",
       "        vertical-align: top;\n",
       "    }\n",
       "\n",
       "    .dataframe thead th {\n",
       "        text-align: right;\n",
       "    }\n",
       "</style>\n",
       "<table border=\"1\" class=\"dataframe\">\n",
       "  <thead>\n",
       "    <tr style=\"text-align: right;\">\n",
       "      <th></th>\n",
       "      <th>stop_id</th>\n",
       "      <th>stop_code</th>\n",
       "      <th>stop_name</th>\n",
       "      <th>stop_desc</th>\n",
       "      <th>zone_id</th>\n",
       "      <th>stop_url</th>\n",
       "      <th>location_type</th>\n",
       "      <th>parent_station</th>\n",
       "      <th>stop_timezone</th>\n",
       "      <th>wheelchair_boarding</th>\n",
       "      <th>geometry</th>\n",
       "    </tr>\n",
       "  </thead>\n",
       "  <tbody>\n",
       "    <tr>\n",
       "      <th>0</th>\n",
       "      <td>stop_183_6119</td>\n",
       "      <td>NaN</td>\n",
       "      <td>Bratysławska</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>0</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>POINT (19.93416 50.08373)</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>1</th>\n",
       "      <td>stop_183_6129</td>\n",
       "      <td>NaN</td>\n",
       "      <td>Bratysławska</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>0</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>POINT (19.93358 50.08465)</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>2</th>\n",
       "      <td>stop_184_6319</td>\n",
       "      <td>NaN</td>\n",
       "      <td>Krowodrza Górka</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>0</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>POINT (19.93126 50.08873)</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>3</th>\n",
       "      <td>stop_186_7019</td>\n",
       "      <td>NaN</td>\n",
       "      <td>Dworzec Towarowy</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>0</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>POINT (19.94029 50.07599)</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>4</th>\n",
       "      <td>stop_186_7029</td>\n",
       "      <td>NaN</td>\n",
       "      <td>Dworzec Towarowy</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>0</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>POINT (19.94033 50.07594)</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>5</th>\n",
       "      <td>stop_186_7039</td>\n",
       "      <td>NaN</td>\n",
       "      <td>Dworzec Towarowy</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>0</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>POINT (19.93968 50.07499)</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>6</th>\n",
       "      <td>stop_187_7119</td>\n",
       "      <td>NaN</td>\n",
       "      <td>Nowy Kleparz</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>0</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>POINT (19.93663 50.07349)</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>7</th>\n",
       "      <td>stop_187_7129</td>\n",
       "      <td>NaN</td>\n",
       "      <td>Nowy Kleparz</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>0</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>POINT (19.93645 50.07351)</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>8</th>\n",
       "      <td>stop_188_7219</td>\n",
       "      <td>NaN</td>\n",
       "      <td>Pędzichów</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>0</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>POINT (19.93754 50.06968)</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>9</th>\n",
       "      <td>stop_188_7229</td>\n",
       "      <td>NaN</td>\n",
       "      <td>Pędzichów</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>0</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>POINT (19.93750 50.06965)</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>10</th>\n",
       "      <td>stop_189_7319</td>\n",
       "      <td>NaN</td>\n",
       "      <td>Politechnika</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>0</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>POINT (19.94506 50.07134)</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>11</th>\n",
       "      <td>stop_189_7329</td>\n",
       "      <td>NaN</td>\n",
       "      <td>Politechnika</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>0</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>POINT (19.94506 50.07081)</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>12</th>\n",
       "      <td>stop_189_7339</td>\n",
       "      <td>NaN</td>\n",
       "      <td>Politechnika</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>0</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>POINT (19.94507 50.07114)</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>13</th>\n",
       "      <td>stop_189_7349</td>\n",
       "      <td>NaN</td>\n",
       "      <td>Politechnika</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>0</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>POINT (19.94502 50.07106)</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>14</th>\n",
       "      <td>stop_191_7719</td>\n",
       "      <td>NaN</td>\n",
       "      <td>Teatr Bagatela</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>0</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>POINT (19.93265 50.06310)</td>\n",
       "    </tr>\n",
       "  </tbody>\n",
       "</table>\n",
       "</div>"
      ],
      "text/plain": [
       "          stop_id stop_code         stop_name stop_desc zone_id stop_url  \\\n",
       "0   stop_183_6119       NaN      Bratysławska       NaN     NaN      NaN   \n",
       "1   stop_183_6129       NaN      Bratysławska       NaN     NaN      NaN   \n",
       "2   stop_184_6319       NaN   Krowodrza Górka       NaN     NaN      NaN   \n",
       "3   stop_186_7019       NaN  Dworzec Towarowy       NaN     NaN      NaN   \n",
       "4   stop_186_7029       NaN  Dworzec Towarowy       NaN     NaN      NaN   \n",
       "5   stop_186_7039       NaN  Dworzec Towarowy       NaN     NaN      NaN   \n",
       "6   stop_187_7119       NaN      Nowy Kleparz       NaN     NaN      NaN   \n",
       "7   stop_187_7129       NaN      Nowy Kleparz       NaN     NaN      NaN   \n",
       "8   stop_188_7219       NaN         Pędzichów       NaN     NaN      NaN   \n",
       "9   stop_188_7229       NaN         Pędzichów       NaN     NaN      NaN   \n",
       "10  stop_189_7319       NaN      Politechnika       NaN     NaN      NaN   \n",
       "11  stop_189_7329       NaN      Politechnika       NaN     NaN      NaN   \n",
       "12  stop_189_7339       NaN      Politechnika       NaN     NaN      NaN   \n",
       "13  stop_189_7349       NaN      Politechnika       NaN     NaN      NaN   \n",
       "14  stop_191_7719       NaN    Teatr Bagatela       NaN     NaN      NaN   \n",
       "\n",
       "    location_type parent_station stop_timezone  wheelchair_boarding  \\\n",
       "0               0            NaN           NaN                  NaN   \n",
       "1               0            NaN           NaN                  NaN   \n",
       "2               0            NaN           NaN                  NaN   \n",
       "3               0            NaN           NaN                  NaN   \n",
       "4               0            NaN           NaN                  NaN   \n",
       "5               0            NaN           NaN                  NaN   \n",
       "6               0            NaN           NaN                  NaN   \n",
       "7               0            NaN           NaN                  NaN   \n",
       "8               0            NaN           NaN                  NaN   \n",
       "9               0            NaN           NaN                  NaN   \n",
       "10              0            NaN           NaN                  NaN   \n",
       "11              0            NaN           NaN                  NaN   \n",
       "12              0            NaN           NaN                  NaN   \n",
       "13              0            NaN           NaN                  NaN   \n",
       "14              0            NaN           NaN                  NaN   \n",
       "\n",
       "                     geometry  \n",
       "0   POINT (19.93416 50.08373)  \n",
       "1   POINT (19.93358 50.08465)  \n",
       "2   POINT (19.93126 50.08873)  \n",
       "3   POINT (19.94029 50.07599)  \n",
       "4   POINT (19.94033 50.07594)  \n",
       "5   POINT (19.93968 50.07499)  \n",
       "6   POINT (19.93663 50.07349)  \n",
       "7   POINT (19.93645 50.07351)  \n",
       "8   POINT (19.93754 50.06968)  \n",
       "9   POINT (19.93750 50.06965)  \n",
       "10  POINT (19.94506 50.07134)  \n",
       "11  POINT (19.94506 50.07081)  \n",
       "12  POINT (19.94507 50.07114)  \n",
       "13  POINT (19.94502 50.07106)  \n",
       "14  POINT (19.93265 50.06310)  "
      ]
     },
     "execution_count": 260,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "feed.stops.head(15)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 261,
   "id": "d133db7a-5608-4e3a-96eb-fd3c10d5f3a0",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/html": [
       "<div>\n",
       "<style scoped>\n",
       "    .dataframe tbody tr th:only-of-type {\n",
       "        vertical-align: middle;\n",
       "    }\n",
       "\n",
       "    .dataframe tbody tr th {\n",
       "        vertical-align: top;\n",
       "    }\n",
       "\n",
       "    .dataframe thead th {\n",
       "        text-align: right;\n",
       "    }\n",
       "</style>\n",
       "<table border=\"1\" class=\"dataframe\">\n",
       "  <thead>\n",
       "    <tr style=\"text-align: right;\">\n",
       "      <th></th>\n",
       "      <th>from_stop_id</th>\n",
       "      <th>to_stop_id</th>\n",
       "      <th>transfer_type</th>\n",
       "    </tr>\n",
       "  </thead>\n",
       "  <tbody>\n",
       "  </tbody>\n",
       "</table>\n",
       "</div>"
      ],
      "text/plain": [
       "Empty DataFrame\n",
       "Columns: [from_stop_id, to_stop_id, transfer_type]\n",
       "Index: []"
      ]
     },
     "execution_count": 261,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "feed.transfers"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 262,
   "id": "b3ab9b1f-9276-4c06-a8fb-f90b003edf2c",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/html": [
       "<div>\n",
       "<style scoped>\n",
       "    .dataframe tbody tr th:only-of-type {\n",
       "        vertical-align: middle;\n",
       "    }\n",
       "\n",
       "    .dataframe tbody tr th {\n",
       "        vertical-align: top;\n",
       "    }\n",
       "\n",
       "    .dataframe thead th {\n",
       "        text-align: right;\n",
       "    }\n",
       "</style>\n",
       "<table border=\"1\" class=\"dataframe\">\n",
       "  <thead>\n",
       "    <tr style=\"text-align: right;\">\n",
       "      <th></th>\n",
       "      <th>trip_id</th>\n",
       "      <th>route_id</th>\n",
       "      <th>service_id</th>\n",
       "      <th>trip_headsign</th>\n",
       "      <th>trip_short_name</th>\n",
       "      <th>direction_id</th>\n",
       "      <th>block_id</th>\n",
       "      <th>shape_id</th>\n",
       "      <th>wheelchair_accessible</th>\n",
       "    </tr>\n",
       "  </thead>\n",
       "  <tbody>\n",
       "    <tr>\n",
       "      <th>0</th>\n",
       "      <td>block_77_trip_1_service_4</td>\n",
       "      <td>route_954</td>\n",
       "      <td>service_4</td>\n",
       "      <td>Cm. Rakowicki</td>\n",
       "      <td>NaN</td>\n",
       "      <td>0</td>\n",
       "      <td>block_77</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>1</th>\n",
       "      <td>block_77_trip_2_service_4</td>\n",
       "      <td>route_954</td>\n",
       "      <td>service_4</td>\n",
       "      <td>Salwator</td>\n",
       "      <td>NaN</td>\n",
       "      <td>1</td>\n",
       "      <td>block_77</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>2</th>\n",
       "      <td>block_77_trip_3_service_4</td>\n",
       "      <td>route_954</td>\n",
       "      <td>service_4</td>\n",
       "      <td>Cm. Rakowicki</td>\n",
       "      <td>NaN</td>\n",
       "      <td>0</td>\n",
       "      <td>block_77</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>3</th>\n",
       "      <td>block_77_trip_4_service_4</td>\n",
       "      <td>route_954</td>\n",
       "      <td>service_4</td>\n",
       "      <td>Salwator</td>\n",
       "      <td>NaN</td>\n",
       "      <td>1</td>\n",
       "      <td>block_77</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>4</th>\n",
       "      <td>block_77_trip_5_service_4</td>\n",
       "      <td>route_954</td>\n",
       "      <td>service_4</td>\n",
       "      <td>Cm. Rakowicki</td>\n",
       "      <td>NaN</td>\n",
       "      <td>0</td>\n",
       "      <td>block_77</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>...</th>\n",
       "      <td>...</td>\n",
       "      <td>...</td>\n",
       "      <td>...</td>\n",
       "      <td>...</td>\n",
       "      <td>...</td>\n",
       "      <td>...</td>\n",
       "      <td>...</td>\n",
       "      <td>...</td>\n",
       "      <td>...</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>4353</th>\n",
       "      <td>block_720_trip_5_service_4</td>\n",
       "      <td>route_53</td>\n",
       "      <td>service_4</td>\n",
       "      <td>Czerwone Maki P+R</td>\n",
       "      <td>NaN</td>\n",
       "      <td>0</td>\n",
       "      <td>block_720</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>4354</th>\n",
       "      <td>block_720_trip_6_service_4</td>\n",
       "      <td>route_53</td>\n",
       "      <td>service_4</td>\n",
       "      <td>Plac Centralny im.R.Reagana</td>\n",
       "      <td>NaN</td>\n",
       "      <td>1</td>\n",
       "      <td>block_720</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>4355</th>\n",
       "      <td>block_720_trip_7_service_4</td>\n",
       "      <td>route_53</td>\n",
       "      <td>service_4</td>\n",
       "      <td>Czerwone Maki P+R</td>\n",
       "      <td>NaN</td>\n",
       "      <td>0</td>\n",
       "      <td>block_720</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>4356</th>\n",
       "      <td>block_720_trip_8_service_4</td>\n",
       "      <td>route_53</td>\n",
       "      <td>service_4</td>\n",
       "      <td>Plac Centralny im.R.Reagana</td>\n",
       "      <td>NaN</td>\n",
       "      <td>1</td>\n",
       "      <td>block_720</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>4357</th>\n",
       "      <td>block_720_trip_9_service_4</td>\n",
       "      <td>route_53</td>\n",
       "      <td>service_4</td>\n",
       "      <td>Zajezdnia Nowa Huta</td>\n",
       "      <td>NaN</td>\n",
       "      <td>0</td>\n",
       "      <td>block_720</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "    </tr>\n",
       "  </tbody>\n",
       "</table>\n",
       "<p>4358 rows × 9 columns</p>\n",
       "</div>"
      ],
      "text/plain": [
       "                         trip_id   route_id service_id  \\\n",
       "0      block_77_trip_1_service_4  route_954  service_4   \n",
       "1      block_77_trip_2_service_4  route_954  service_4   \n",
       "2      block_77_trip_3_service_4  route_954  service_4   \n",
       "3      block_77_trip_4_service_4  route_954  service_4   \n",
       "4      block_77_trip_5_service_4  route_954  service_4   \n",
       "...                          ...        ...        ...   \n",
       "4353  block_720_trip_5_service_4   route_53  service_4   \n",
       "4354  block_720_trip_6_service_4   route_53  service_4   \n",
       "4355  block_720_trip_7_service_4   route_53  service_4   \n",
       "4356  block_720_trip_8_service_4   route_53  service_4   \n",
       "4357  block_720_trip_9_service_4   route_53  service_4   \n",
       "\n",
       "                    trip_headsign trip_short_name  direction_id   block_id  \\\n",
       "0                   Cm. Rakowicki             NaN             0   block_77   \n",
       "1                        Salwator             NaN             1   block_77   \n",
       "2                   Cm. Rakowicki             NaN             0   block_77   \n",
       "3                        Salwator             NaN             1   block_77   \n",
       "4                   Cm. Rakowicki             NaN             0   block_77   \n",
       "...                           ...             ...           ...        ...   \n",
       "4353            Czerwone Maki P+R             NaN             0  block_720   \n",
       "4354  Plac Centralny im.R.Reagana             NaN             1  block_720   \n",
       "4355            Czerwone Maki P+R             NaN             0  block_720   \n",
       "4356  Plac Centralny im.R.Reagana             NaN             1  block_720   \n",
       "4357          Zajezdnia Nowa Huta             NaN             0  block_720   \n",
       "\n",
       "     shape_id  wheelchair_accessible  \n",
       "0         NaN                    NaN  \n",
       "1         NaN                    NaN  \n",
       "2         NaN                    NaN  \n",
       "3         NaN                    NaN  \n",
       "4         NaN                    NaN  \n",
       "...       ...                    ...  \n",
       "4353      NaN                    NaN  \n",
       "4354      NaN                    NaN  \n",
       "4355      NaN                    NaN  \n",
       "4356      NaN                    NaN  \n",
       "4357      NaN                    NaN  \n",
       "\n",
       "[4358 rows x 9 columns]"
      ]
     },
     "execution_count": 262,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "feed.trips"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "e09cd5b9-17bb-41e5-90af-039c61a3f8ac",
   "metadata": {},
   "source": [
    "## Planning out the approach"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "7bbaee4c-ca54-4196-bf80-50ebd1b4676c",
   "metadata": {},
   "source": [
    "Our objective is to get a summary of the frequencies between stop pairs"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "2170fa29-6495-424c-abad-4ed594ff4337",
   "metadata": {},
   "source": [
    "***How many times do stop pairs repeat***"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "cac57f18-4f6f-4d34-9134-ef9f4f9436e2",
   "metadata": {},
   "source": [
    "## Execute"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 263,
   "id": "45dabe41-7a92-42d6-9d42-1f8c4fb89381",
   "metadata": {},
   "outputs": [
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "/Users/filip/code/anaconda3/envs/rs/lib/python3.9/site-packages/pandas/core/indexing.py:1667: SettingWithCopyWarning: \n",
      "A value is trying to be set on a copy of a slice from a DataFrame.\n",
      "Try using .loc[row_indexer,col_indexer] = value instead\n",
      "\n",
      "See the caveats in the documentation: https://pandas.pydata.org/pandas-docs/stable/user_guide/indexing.html#returning-a-view-versus-a-copy\n",
      "  self.obj[key] = value\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "Start:   104885 stop_times\n",
      "Shifted: 100527 stop_times\n",
      "DropNA:  100527 stop_times\n",
      "\n",
      "Finally: 5965 trips between 7:30 and 8:30\n"
     ]
    }
   ],
   "source": [
    "# isolate the dataset\n",
    "df = feed.stop_times[[\"trip_id\", \"stop_id\", \"arrival_time\", \"departure_time\"]]\n",
    "print(f\"Start:   {len(df)} stop_times\")\n",
    "\n",
    "# generate the next stop/trip\n",
    "df.loc[:, \"stop_id_next\"] = df.loc[:, \"stop_id\"].shift(-1)\n",
    "df.loc[:, \"trip_id_next\"] = df.loc[:, \"trip_id\"].shift(-1)\n",
    "df = df[df.trip_id == df.trip_id_next]\n",
    "print(f\"Shifted: {len(df)} stop_times\")\n",
    "\n",
    "df = df.dropna() # Drop the last one\n",
    "print(f\"DropNA:  {len(df)} stop_times\\n\")\n",
    "\n",
    "# Filter by study start and end time\n",
    "START_TIME = 7.5 * 60 * 60\n",
    "END_TIME = 8.5 * 60 * 60\n",
    "df = df[(START_TIME <= df.departure_time) & (df.departure_time <= END_TIME)]\n",
    "\n",
    "# get stats\n",
    "stop_stats = df.groupby([\"stop_id\", \"stop_id_next\"]).agg(\"count\")[[\"arrival_time\"]].reset_index().rename({\"arrival_time\": \"trips_per_hour\"}, axis=1)\n",
    "\n",
    "print(f\"Finally: {stop_stats.trips_per_hour.sum()} trips between 7:30 and 8:30\")"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "59dc66f5-013b-4ca4-9852-9ad19cb34900",
   "metadata": {},
   "source": [
    "# Combine"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "53848b22-8164-44ac-9fdb-81c4a2169532",
   "metadata": {},
   "source": [
    "## Merge"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 264,
   "id": "8b375b03-916c-45e7-be24-767ac0d62a89",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "'LYJ04_'"
      ]
     },
     "execution_count": 264,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "prefix = list(T.G.edges)[0][0][:6]\n",
    "prefix"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 265,
   "id": "6bbe1eb7-544f-43d0-bd08-a7da02562bd3",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/html": [
       "<div>\n",
       "<style scoped>\n",
       "    .dataframe tbody tr th:only-of-type {\n",
       "        vertical-align: middle;\n",
       "    }\n",
       "\n",
       "    .dataframe tbody tr th {\n",
       "        vertical-align: top;\n",
       "    }\n",
       "\n",
       "    .dataframe thead th {\n",
       "        text-align: right;\n",
       "    }\n",
       "</style>\n",
       "<table border=\"1\" class=\"dataframe\">\n",
       "  <thead>\n",
       "    <tr style=\"text-align: right;\">\n",
       "      <th></th>\n",
       "      <th>source</th>\n",
       "      <th>target</th>\n",
       "      <th>length</th>\n",
       "      <th>trips_per_hour</th>\n",
       "      <th>mode</th>\n",
       "    </tr>\n",
       "  </thead>\n",
       "  <tbody>\n",
       "    <tr>\n",
       "      <th>0</th>\n",
       "      <td>LYJ04_stop_1058_345919</td>\n",
       "      <td>LYJ04_stop_212_13519</td>\n",
       "      <td>120.0</td>\n",
       "      <td>NaN</td>\n",
       "      <td>transit</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>1</th>\n",
       "      <td>LYJ04_stop_1058_345929</td>\n",
       "      <td>LYJ04_stop_210_13329</td>\n",
       "      <td>120.0</td>\n",
       "      <td>NaN</td>\n",
       "      <td>transit</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>2</th>\n",
       "      <td>LYJ04_stop_1076_317419</td>\n",
       "      <td>LYJ04_stop_263_45319</td>\n",
       "      <td>60.0</td>\n",
       "      <td>NaN</td>\n",
       "      <td>transit</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>3</th>\n",
       "      <td>LYJ04_stop_1076_317429</td>\n",
       "      <td>LYJ04_stop_261_45129</td>\n",
       "      <td>60.0</td>\n",
       "      <td>NaN</td>\n",
       "      <td>transit</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>4</th>\n",
       "      <td>LYJ04_stop_1102_347019</td>\n",
       "      <td>LYJ04_stop_325_136019</td>\n",
       "      <td>120.0</td>\n",
       "      <td>NaN</td>\n",
       "      <td>transit</td>\n",
       "    </tr>\n",
       "  </tbody>\n",
       "</table>\n",
       "</div>"
      ],
      "text/plain": [
       "                   source                 target  length  trips_per_hour  \\\n",
       "0  LYJ04_stop_1058_345919   LYJ04_stop_212_13519   120.0             NaN   \n",
       "1  LYJ04_stop_1058_345929   LYJ04_stop_210_13329   120.0             NaN   \n",
       "2  LYJ04_stop_1076_317419   LYJ04_stop_263_45319    60.0             NaN   \n",
       "3  LYJ04_stop_1076_317429   LYJ04_stop_261_45129    60.0             NaN   \n",
       "4  LYJ04_stop_1102_347019  LYJ04_stop_325_136019   120.0             NaN   \n",
       "\n",
       "      mode  \n",
       "0  transit  \n",
       "1  transit  \n",
       "2  transit  \n",
       "3  transit  \n",
       "4  transit  "
      ]
     },
     "execution_count": 265,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "T.edges_df.head()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 266,
   "id": "13beecb1-f005-400e-9d7d-c0fa43a5491d",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/html": [
       "<div>\n",
       "<style scoped>\n",
       "    .dataframe tbody tr th:only-of-type {\n",
       "        vertical-align: middle;\n",
       "    }\n",
       "\n",
       "    .dataframe tbody tr th {\n",
       "        vertical-align: top;\n",
       "    }\n",
       "\n",
       "    .dataframe thead th {\n",
       "        text-align: right;\n",
       "    }\n",
       "</style>\n",
       "<table border=\"1\" class=\"dataframe\">\n",
       "  <thead>\n",
       "    <tr style=\"text-align: right;\">\n",
       "      <th></th>\n",
       "      <th>stop_id</th>\n",
       "      <th>stop_id_next</th>\n",
       "      <th>trips_per_hour</th>\n",
       "    </tr>\n",
       "  </thead>\n",
       "  <tbody>\n",
       "    <tr>\n",
       "      <th>0</th>\n",
       "      <td>stop_1058_345919</td>\n",
       "      <td>stop_212_13519</td>\n",
       "      <td>16</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>1</th>\n",
       "      <td>stop_1058_345929</td>\n",
       "      <td>stop_210_13329</td>\n",
       "      <td>16</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>2</th>\n",
       "      <td>stop_1076_317419</td>\n",
       "      <td>stop_263_45319</td>\n",
       "      <td>8</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>3</th>\n",
       "      <td>stop_1076_317429</td>\n",
       "      <td>stop_261_45129</td>\n",
       "      <td>8</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>4</th>\n",
       "      <td>stop_1102_347019</td>\n",
       "      <td>stop_325_136019</td>\n",
       "      <td>29</td>\n",
       "    </tr>\n",
       "  </tbody>\n",
       "</table>\n",
       "</div>"
      ],
      "text/plain": [
       "            stop_id     stop_id_next  trips_per_hour\n",
       "0  stop_1058_345919   stop_212_13519              16\n",
       "1  stop_1058_345929   stop_210_13329              16\n",
       "2  stop_1076_317419   stop_263_45319               8\n",
       "3  stop_1076_317429   stop_261_45129               8\n",
       "4  stop_1102_347019  stop_325_136019              29"
      ]
     },
     "execution_count": 266,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "stop_stats.head()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 267,
   "id": "b8b7e3ed-4a7e-47ed-95ea-c665e0280144",
   "metadata": {},
   "outputs": [],
   "source": [
    "for (_, row) in stop_stats.iterrows():\n",
    "    source = prefix + row[\"stop_id\"]\n",
    "    target = prefix + row[\"stop_id_next\"]\n",
    "    trips_per_hour = row[\"trips_per_hour\"]\n",
    "    \n",
    "    T.G[source][target][0][\"trips_per_hour\"] = trips_per_hour"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 268,
   "id": "ba38ba6d-7cc5-411e-a2e1-4c56cb6deae7",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/html": [
       "<div>\n",
       "<style scoped>\n",
       "    .dataframe tbody tr th:only-of-type {\n",
       "        vertical-align: middle;\n",
       "    }\n",
       "\n",
       "    .dataframe tbody tr th {\n",
       "        vertical-align: top;\n",
       "    }\n",
       "\n",
       "    .dataframe thead th {\n",
       "        text-align: right;\n",
       "    }\n",
       "</style>\n",
       "<table border=\"1\" class=\"dataframe\">\n",
       "  <thead>\n",
       "    <tr style=\"text-align: right;\">\n",
       "      <th></th>\n",
       "      <th>source</th>\n",
       "      <th>target</th>\n",
       "      <th>length</th>\n",
       "      <th>trips_per_hour</th>\n",
       "      <th>mode</th>\n",
       "    </tr>\n",
       "  </thead>\n",
       "  <tbody>\n",
       "    <tr>\n",
       "      <th>210</th>\n",
       "      <td>LYJ04_stop_267_45919</td>\n",
       "      <td>LYJ04_stop_274_46619</td>\n",
       "      <td>240.0</td>\n",
       "      <td>NaN</td>\n",
       "      <td>transit</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>211</th>\n",
       "      <td>LYJ04_stop_267_45929</td>\n",
       "      <td>LYJ04_stop_253_42329</td>\n",
       "      <td>240.0</td>\n",
       "      <td>NaN</td>\n",
       "      <td>transit</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>300</th>\n",
       "      <td>LYJ04_stop_314_92259</td>\n",
       "      <td>LYJ04_stop_294_61419</td>\n",
       "      <td>60.0</td>\n",
       "      <td>NaN</td>\n",
       "      <td>transit</td>\n",
       "    </tr>\n",
       "  </tbody>\n",
       "</table>\n",
       "</div>"
      ],
      "text/plain": [
       "                   source                target  length  trips_per_hour  \\\n",
       "210  LYJ04_stop_267_45919  LYJ04_stop_274_46619   240.0             NaN   \n",
       "211  LYJ04_stop_267_45929  LYJ04_stop_253_42329   240.0             NaN   \n",
       "300  LYJ04_stop_314_92259  LYJ04_stop_294_61419    60.0             NaN   \n",
       "\n",
       "        mode  \n",
       "210  transit  \n",
       "211  transit  \n",
       "300  transit  "
      ]
     },
     "execution_count": 268,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "# Missing trips data\n",
    "T.edges_df[T.edges_df.trips_per_hour.isna()]"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "2369ef46-fe43-43e8-a006-1e3ebba7b7d6",
   "metadata": {},
   "source": [
    "# Visualize"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "be46545b-9439-44bb-9388-97629faf3532",
   "metadata": {},
   "source": [
    "approach:\n",
    "```\n",
    "Using matplotlib\n",
    "Make linestrings from Origin Points and target points\n",
    "add back to the edges_df\n",
    "```"

    "1. Load GTFS data\n",
    "2. Process using Transit + OSMnx  \n",
    "(3. Test and refactor code as needed.)\n",
    "4. Visualize schedule\n",
    "5. Share\n",
    "----\n",
    "6. Experiment with summary statistics"

   ]
  },
  {
   "cell_type": "markdown",

   "id": "467d33f5-4e6e-413e-b676-48fcbbff24ff",
   "metadata": {},
   "source": [
    "## Map it"

   "id": "7fe25012-5b54-468a-b4ba-239c58779ef5",
   "metadata": {},
   "source": [
    "## Setup"

   ]
  },
  {
   "cell_type": "code",

   "execution_count": 269,
   "id": "83af3f4a-3f00-4ea1-a8fd-6dc2f417ebb1",
   "metadata": {},
   "outputs": [],
   "source": [
    "lines = T.edges_df\n",
    "stops = T.nodes_df"

   "execution_count": 2,
   "id": "72cc5fd1-776a-4223-8e76-5dba1702198b",
   "metadata": {},
   "outputs": [],
   "source": [
    "import os"

   ]
  },
  {
   "cell_type": "code",

   "execution_count": 270,
   "id": "5e5a96b7-79d4-4aeb-a8be-de21468b2ed9",
   "metadata": {},
   "outputs": [],
   "source": [
    "from shapely.geometry import Point, LineString"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 271,
   "id": "823ba638-2167-4f4c-9a69-fe7542f8c4ba",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "<class 'pandas.core.frame.DataFrame'>\n",
      "RangeIndex: 331 entries, 0 to 330\n",
      "Data columns (total 3 columns):\n",
      " #   Column  Non-Null Count  Dtype  \n",
      "---  ------  --------------  -----  \n",
      " 0   id      331 non-null    object \n",
      " 1   y       331 non-null    float64\n",
      " 2   x       331 non-null    float64\n",
      "dtypes: float64(2), object(1)\n",
      "memory usage: 7.9+ KB\n"
     ]
    }
   ],
   "source": [
    "stops.info()"

   "execution_count": 3,
   "id": "36144bd4-f7c2-4d78-9437-48b948cf85d1",
   "metadata": {},
   "outputs": [],
   "source": [
    "os.chdir(os.path.dirname(os.getcwd()))"

   ]
  },
  {
   "cell_type": "code",

   "execution_count": 272,
   "id": "a78d10b7-b5dc-466b-8464-4504aa1c4ae0",
   "metadata": {},
   "outputs": [],
   "source": [
    "# Make stops xy into shapely points\n",
    "stops[\"geometry\"] = stops.apply(lambda pt: Point(pt[\"x\"], pt[\"y\"]), axis=1)"

   "execution_count": 5,
   "id": "b0c94074-c315-4bfc-a71d-5f8b1417cf71",
   "metadata": {},
   "outputs": [],
   "source": [
    "from final_project.network import WalkNetwork, TransitNetwork, MultiNetwork"

   ]
  },
  {
   "cell_type": "code",

   "execution_count": 273,
   "id": "dadc0880-47cf-4ddf-be52-d5e2c86a9388",
   "metadata": {},
   "outputs": [],
   "source": [
    "# add these points to the lines df\n",
    "lines = lines.merge(stops[[\"id\", \"geometry\"]].rename({\"id\":\"source\", \"geometry\":\"source_geom\"}, axis=1), on=\"source\").merge(stops[[\"id\", \"geometry\"]].rename({\"id\":\"target\", \"geometry\":\"target_geom\"}, axis=1), on=\"target\")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 274,
   "id": "8ee8514e-a554-452b-942c-ebfe50bc7134",
   "metadata": {},
   "outputs": [],
   "source": [
    "# Make point geometries into lines\n",
    "lines[\"geometry\"] = lines.apply(lambda pt: LineString([pt.source_geom, pt.target_geom]), axis=1)"

   "execution_count": 8,
   "id": "5d55fc9d-b6d9-42b2-987e-e05316030e9f",
   "metadata": {},
   "outputs": [],
   "source": [
    "data_2019 = os.path.join(\"demo\", \"data\", \"krakow_tram_20210901.zip\")"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "5b5e67f9-8043-4ee7-919d-2391eaea8afb",
   "metadata": {},
   "source": [
    "## Load data"

   ]
  },
  {
   "cell_type": "code",

   "execution_count": 276,
   "id": "80460fc0-b6e9-485a-a5ca-33e1971581ed",
   "metadata": {},
   "outputs": [],
   "source": [
    "# Drop redundant columns\n",
    "lines = lines.drop([\"source_geom\", \"target_geom\"], axis=1)"

   "execution_count": 9,
   "id": "7a1648e3-e26e-4deb-ae8a-aaa8d7767b1f",
   "metadata": {},
   "outputs": [],
   "source": [
    "T = TransitNetwork.create_from_gtfs(data_2019)"

   ]
  },
  {
   "cell_type": "code",

   "execution_count": 277,
   "id": "797a16c8-3296-41f1-ba14-9dc7ca8e5a44",
   "metadata": {},
   "outputs": [],
   "source": [
    "# Convert to GeoDataFrame\n",
    "lines_gdf = gpd.GeoDataFrame(lines)\n",
    "lines_gdf = lines_gdf.set_crs(\"EPSG:4326\")\n",
    "lines_gdf = lines_gdf.to_crs(\"EPSG:3857\")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 282,
   "id": "9d469f0b-a537-4557-99d1-7d85b14d9b6d",
   "metadata": {
    "tags": []
   },
   "outputs": [
    {
     "data": {
      "text/plain": [
       "Text(0.5, 1.0, 'Trams per hour, Kraków')"
      ]
     },
     "execution_count": 282,
     "metadata": {},
     "output_type": "execute_result"
    },
    {
     "data": {
      "image/png": "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HwK/d/fflP5+0m3d/X5g2pDbrAROcPfWA39IIiIiMuZSVTDQhnuM2WT+6iQiIiJ7MtwpEpcAPy1NgVgBvN7M3gbg7rv2Xdjrbfc3WBERERmnMg0hwdC7GauaUe5oREREpAyGlWBw93sIyyCG2m1iwd1fN4zb7nqbBcOJQ0RERMapymnQuQK6N4ASDCIiIns01o0Xx5JqGEVEROTAVc0MP/s08UlERGSqGu4SCREREZE9skwtDpDrKHcoIiIi49pkPso/mR+biIiIjBGzCKIU5Htx93KHIyIiImWgCgYREREZGakqGGiHQh+kKssdjYiIyLgz2cdUTubHJiIiImMp0wCA920tcyAiIiJSDkowiIiIyMiobAk/ezeWNw4REREpCy2REBERkRFh2abQ6LGvtdyhiIiIjFsaUykiIiKyN+na8DPXXtYwREREpDxUwSAiIiIjI1kBFkGhH48LWKSvGSIiIruazEf5J/NjExERkTFkZpCsCn8MtJU3GBERERlzOrQgIiIiIydTD/ku6G+DipZyRyMiIjKuaEyliIiIyHBlGwFwNXoUERGZcpRgEBERkRFj2frwixIMIiIiU46WSIiIiMjIGZwkMdCOu4e+DCIiIrLdZP5kVAWDiIiIjJzBBEMyi8f58sYiIiIiY0oVDCIiIjJiLJHGLQn5HixKlTscERGRcceiMa5hiH3M7koVDCIiIjKyoiRYpOURIiIiU4wqGERERGTkuZILIiIiuzP2Cfixq2BQgkFERERGViEHhYFyRyEiIiJjTEskREREZGQV85BIlzsKERERGWOqYBAREZER4x6DFyFRWe5QRERExh0ziMa6yWNx7O5KFQwiIiIycgp94A7JinJHIiIiImNMFQwiIiIyYjzfG35JqYJBRERkdybzlCVVMIiIiMjIyXWFn6nq8sYhIiIiY04VDCIiIjJyBjrCz0xteeMQEREZlwwb6x4MY0gVDCIiIjJycp3hZ7quvHGIiIjImFOCQUREREZOvgcAy9SUORAREREZa1oiISIiIiNnsMljUk0eRUREdkdNHkVERESGo9APgEepMgciIiIiY00VDCIiIjJyqmdD10roWgV1B5U7GhERkfHFUJNHERERkWFpXArEsP5mPC6UOxoREREZQ0owiIiIyIiJamZDdhrEOXzzXeUOR0REZFwxQg+GsTyNJSUYRERExlDc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\n",
      "text/plain": [
       "<Figure size 1440x792 with 2 Axes>"
      ]
     },
     "metadata": {
      "needs_background": "light"
     },
     "output_type": "display_data"
    }
   ],
   "source": [
    "# plot\n",
    "fig, ax = plt.subplots(figsize=(20,11))\n",
    "lines_gdf.plot(ax=ax, column=\"trips_per_hour\", legend=True, cmap='OrRd')\n",
    "ax.set_title(\"Trams per hour, Kraków\", fontsize=20)"

   "execution_count": 10,
   "id": "b11a51b5-714c-494b-aa97-b8f8510a22eb",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/html": [
      ],
      "text/plain": [
       "<folium.folium.Map at 0x168d6beb0>"
      ]
     },
     "execution_count": 10,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "T.mapper"

   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,

   "id": "71f93806-5857-459d-b53b-d86423d426d2",

   "id": "cd6fb7ab-4924-4b48-a20e-e3966dda55e7",

   "metadata": {},
   "outputs": [],
   "source": []
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3 (ipykernel)",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.9.7"

  },
  "toc-autonumbering": true

  }

 },
 "nbformat": 4,
 "nbformat_minor": 5
}