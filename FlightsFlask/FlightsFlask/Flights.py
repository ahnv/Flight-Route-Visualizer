import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import matplotlib.lines as mlines
import os
import requests

class Flights(object):
    """description of class"""

    def __init__(self):
        airport_col = ['ID', 'Name', 'City', 'Country','IATA', 'ICAO', 'Lat', 'Long', 'Alt', 'Timezone', 'DST', 'Tz database time zone', 'type', 'source']
        try:
            self.airport_df = pd.read_pickle('airport.pkl')
        except Exception:
            self.airport_df = pd.read_csv("https://raw.githubusercontent.com/jpatokal/openflights/master/data/airports.dat", names = airport_col, index_col = 0)
            self.airport_df.to_pickle('airport.pkl')

        
        route_cols = ['Airline', 'Airline ID', 'Source Airport', 'Source Airport ID', 'Dest Airport', 'Dest Airport ID', 'Codeshare', 'Stops', 'equipment']
        
        try:
            self.routes_df = pd.read_pickle('routes.pkl')
        except Exception:
            self.routes_df = pd.read_csv("https://raw.githubusercontent.com/jpatokal/openflights/master/data/routes.dat", names = route_cols)
            self.routes_df.to_pickle('routes.pkl')

        self.routes_df['Source Airport ID'] = pd.to_numeric(self.routes_df['Source Airport ID'].astype(str), 'coerce')
        self.routes_df['Dest Airport ID'] = pd.to_numeric(self.routes_df['Dest Airport ID'].astype(str), 'coerce')
        self.routes_df = self.routes_df.dropna(subset=["Source Airport ID", "Dest Airport ID"]) 

    def check_if_country_exists(self,country = None):
        if (self.airport_df is None) or (self.routes_df is None) or (country is None) or (country is ""):
            return -1
        airports = self.airport_df[(self.airport_df.Country == country)][['Name','Lat', 'Long', 'IATA', 'ICAO']]
        airports_ix = airports.index.values
        routes = self.routes_df[(self.routes_df['Source Airport ID'].isin(airports_ix)) & (self.routes_df['Dest Airport ID'].isin(airports_ix))]
        routes =  pd.DataFrame(routes.groupby(['Source Airport', 'Dest Airport']).size().reset_index(name='counts'))

        counts = routes['Source Airport'].append(routes.loc[routes['Source Airport'] != routes['Dest Airport'], 'Dest Airport']).value_counts()

        return len(counts)

    def simple_visualization(self, country = None):
        if (self.airport_df is None) or (self.routes_df is None):
            print("Cannot Retrieve Data")
        else:
            if os.path.isfile("./FlightsFlask/static/images/"+country+"/map_1.png") and os.path.isfile("./FlightsFlask/static/images/"+country+"/map_2.png"):
                return 1
            r = requests.get(url = "https://nominatim.openstreetmap.org/search?format=json&q="+country) 
            data = r.json()
            data = data[0]['boundingbox']
            airports = self.airport_df[(self.airport_df.Country == country)][['Name','Lat', 'Long', 'IATA', 'ICAO']]
            airports_ix = airports.index.values

            routes = self.routes_df[(self.routes_df['Source Airport ID'].isin(airports_ix)) & (self.routes_df['Dest Airport ID'].isin(airports_ix))]
            routes =  pd.DataFrame(routes.groupby(['Source Airport', 'Dest Airport']).size().reset_index(name='counts'))

            counts = routes['Source Airport'].append(routes.loc[routes['Source Airport'] != routes['Dest Airport'], 'Dest Airport']).value_counts()

            counts = pd.DataFrame({'IATA': counts.index, 'total_flight': counts})
            pos_data = counts.merge(airports, on = 'IATA')

            graph = nx.from_pandas_edgelist(routes, source = 'Source Airport', target = 'Dest Airport', edge_attr = 'counts',create_using = nx.DiGraph())

            plt.figure(figsize = (10,9))
            nx.draw_networkx(graph)
            
            if not os.path.isdir("./FlightsFlask/static/images/"+country):
                os.makedirs("./FlightsFlask/static/images/"+country)
            plt.savefig("./FlightsFlask/static/images/"+country+"/map_1.png", format = "png", dpi = 300)
            #plt.show()

            plt.figure(figsize=(15,20))
            m = Basemap(
		        projection='merc',
		        llcrnrlon=float(data[2]),
		        llcrnrlat=float(data[0]),
		        urcrnrlon=float(data[3]),
		        urcrnrlat=float(data[1]),
		        lat_ts=0,
		        resolution='l',
		        suppress_ticks=True)

            mx, my = m(pos_data['Long'].values, pos_data['Lat'].values)
            pos = {}
            for count, elem in enumerate (pos_data['IATA']):
                pos[elem] = (mx[count], my[count])
             
            nx.draw_networkx_nodes(G = graph, pos = pos, node_list = graph.nodes(), node_color = 'r', alpha = 0.8, node_size = [counts['total_flight'][s]*3 for s in graph.nodes()])
            nx.draw_networkx_edges(G = graph, pos = pos, edge_color='g', width = routes['counts']*0.75, alpha=0.2, arrows = False)
            m.drawcountries(linewidth = 3)
            m.drawstates(linewidth = 0.2)
            m.drawcoastlines(linewidth=3)
            plt.tight_layout()
            if not os.path.isdir("./FlightsFlask/static/images/"+country):
                os.makedirs("./FlightsFlask/static/images/"+country)
            plt.savefig("./FlightsFlask/static/images/"+country+"/map_2.png", format = "png", dpi = 300)
            #plt.show()
            print ("successful visualization")
            return 1
    
    def advanced_visualization(self, country = None):
        if (self.airport_df is None) or (self.routes_df is None):
            print("Cannot Retrieve Data")
        else:
            if os.path.isfile("./FlightsFlask/static/images/"+country+"/map_3.png"):
                return 1
            r = requests.get(url = "https://nominatim.openstreetmap.org/search?format=json&q="+country) 
            data = r.json()
            data = data[0]['boundingbox']
            airport = self.airport_df[(self.airport_df.Country == country)]
            airport_ix = airport.index.values
            
            routes = self.routes_df[(self.routes_df['Source Airport ID'].isin(airport_ix)) & (self.routes_df['Dest Airport ID'].isin(airport_ix))]
            routes =  pd.DataFrame(routes.groupby(['Source Airport', 'Dest Airport']).size().reset_index(name='counts'))
            
            counts = routes['Source Airport'].append(routes.loc[routes['Source Airport'] != routes['Dest Airport'], 'Dest Airport']).value_counts()

            counts = pd.DataFrame({'IATA': counts.index, 'total_flight': counts})
            pos_data = counts.merge(airport, on = 'IATA')

            graph = nx.from_pandas_edgelist(routes, source = 'Source Airport', target = 'Dest Airport', edge_attr = 'counts',create_using = nx.DiGraph())
            plt.figure(figsize=(15,20))

            m = Basemap(
		        projection='merc',
		        llcrnrlon=float(data[2]),
		        llcrnrlat=float(data[0]),
		        urcrnrlon=float(data[3]),
		        urcrnrlat=float(data[1]),
		        lat_ts=0,
		        resolution='l',
		        suppress_ticks=True)
            mx, my = m(pos_data['Long'].values, pos_data['Lat'].values)

            pos = {}
            for count, elem in enumerate (pos_data['IATA']):
                pos[elem] = (mx[count], my[count])

            nx.draw_networkx_nodes(G = graph, pos = pos, nodelist = [x for x in graph.nodes() if counts['total_flight'][x] >= 25], node_color = 'r', alpha = 0.8, node_size = [counts['total_flight'][x]*4  for x in graph.nodes() if counts['total_flight'][x] >= 100])

            nx.draw_networkx_labels(G = graph, pos = pos, font_size=10, labels = {x:x for x in graph.nodes() if counts['total_flight'][x] >= 50})

            nx.draw_networkx_nodes(G = graph, pos = pos, nodelist = [x for x in graph.nodes() if counts['total_flight'][x] < 25], node_color = 'b', alpha = 0.6, node_size = [counts['total_flight'][x]*4  for x in graph.nodes() if counts['total_flight'][x] < 100])

            nx.draw_networkx_edges(G = graph, pos = pos, edge_color = 'g', width = routes['counts']*0.75, alpha=0.06, arrows = False)

            m.drawcountries(linewidth = 3)
            m.drawstates(linewidth = 0.2)
            m.drawcoastlines(linewidth=1)
            m.fillcontinents(alpha = 0.3)
            line1 = mlines.Line2D(range(1), range(1), color="white", marker='o', markerfacecolor="red")
            line2 = mlines.Line2D(range(1), range(1), color="white", marker='o',markerfacecolor="blue")
            line3 = mlines.Line2D(range(1), range(1), color="green", marker='',markerfacecolor="green")
            plt.legend((line1, line2, line3), ('Large Airport > 25 routes', 'Smaller airports', 'routes'), loc=4, fontsize = 'xx-large')
            plt.title("Network graph of flight routes in India", fontsize = 30)
            plt.tight_layout()
            if not os.path.isdir("./FlightsFlask/static/images/"+country):
                os.makedirs("./FlightsFlask/static/images/"+country)
            plt.savefig("./FlightsFlask/static/images/"+country+"/map_3.png", format = "png", dpi = 300)
            #plt.show()
            print ("successful visualization")
            return 1

    def analysis(self, country = None):
        if (self.airport_df is None) or (self.routes_df is None):
            print("Cannot Retrieve Data")
        else:
            airport = self.airport_df[(self.airport_df.Country == country)]
            airport_ix = airport.index.values
            
            routes = self.routes_df[(self.routes_df['Source Airport ID'].isin(airport_ix)) & (self.routes_df['Dest Airport ID'].isin(airport_ix))]
            routes =  pd.DataFrame(routes.groupby(['Source Airport', 'Dest Airport']).size().reset_index(name='counts'))
            
            counts = routes['Source Airport'].append(routes.loc[routes['Source Airport'] != routes['Dest Airport'], 'Dest Airport']).value_counts()

            counts = pd.DataFrame({'IATA': counts.index, 'total_flight': counts})
            pos_data = counts.merge(airport, on = 'IATA')
            graph = nx.from_pandas_edgelist(routes, source = 'Source Airport', target = 'Dest Airport', edge_attr = 'counts',create_using = nx.DiGraph())

            data = {}

            try:
                data["Average Shortest Path Length"] = nx.average_shortest_path_length(graph)
            except Exception:
                data["Average Shortest Path Length"] = None

            try:
                data["Diameter"] = nx.diameter(graph)
            except Exception:
                data["Diameter"] = None

            try:
                data["Eccentricity"] = nx.eccentricity(graph)
            except Exception:
                data["Eccentricity"] = None

            try:
                data["Radius"] = nx.radius(graph)
            except Exception:
                data["Radius"] = None

            try:
                data["Periphery"] = nx.periphery(graph)
            except Exception:
                data["Periphery"] = None

            try:
                data["Center"] = nx.center(graph)
            except Exception:
                data["Center"] = None

            try:
                data["Average Clustering"] = nx.average_clustering(graph)
            except Exception:
                data["Average Clustering"] = None

            try:
                data["Transitivity"] = nx.transitivity(graph)
            except Exception:
                data["Transitivity"] = None

            try:
                data["Number Connected Components"] = nx.number_connected_components(graph)
            except Exception:
                data["Number Connected Components"] = None

            try:
                data["Strongly Connected"] = not nx.is_weakly_connected(graph)
            except Exception:
                data["Strongly Connected"] = None

            try:
                data["Weakly Connected"] = nx.is_weakly_connected(graph)
            except Exception:
                data["Weakly Connected"] = None

            try:
                data["Node Connectivity"] = nx.node_connectivity(graph)
            except Exception:
                data["Node Connectivity"] = None

           
            try:
                data["Jaccard Coefficient"] = nx.jaccard_coefficient(graph)
            except Exception:
                data["Jaccard Coefficient"] = None

            try:
                data["Resource Allocation Index"] = nx.resource_allocation_index(graph)
            except Exception:
                data["Resource Allocation Index"] = None

            try:
                data["Adamic Adar Index"] = nx.adamic_adar_index(graph)
            except Exception:
                data["Adamic Adar Index"] = None

            return data
                    
