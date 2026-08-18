import asyncio
import numpy as np
from typing import List, Dict



class Forecast:

    def __init__(self, nr_simulations: int, backlog_min: int, backlog_max:int, capacity:int, throughput: List[int], pool_executor=None):
        if pool_executor is None:
            raise ValueError("pool_executor é obrigatório para usar ProcessPoolExecutor")
        self.nr_simulations = nr_simulations
        self.backlog_min = backlog_min
        self.backlog_max = backlog_max
        self.capacity = capacity
        self.throughput = throughput
        self.pool_executor = pool_executor



    async def run_forecast(self) -> dict:
        
        throughput_forecast = self.get_capacity_throughput()
        forecast_weeks = await self.run_simulations(throughput_forecast)
        percentiles = self.calculate_percentiles(forecast_weeks,[50,75,85,95])
        response = self.format_forecast_response(
        throughput_forecast=throughput_forecast,
        p50=percentiles[50],
        p75=percentiles[75],
        p85=percentiles[85],
        p95=percentiles[95]
        )
        return response
    
    def get_capacity_throughput(self) -> List[int]:
        throughput = self.throughput
        if self.capacity == 100:
            return list(throughput)
        
        capacity_percentage = self.capacity / 100 

        capacity_throughput = [round(week * capacity_percentage) for week in throughput]
        
        return capacity_throughput

    async def run_simulations(self, throughput_forecast: List[int]) -> List[int]:
        
        loop = asyncio.get_running_loop()
        forecast_weeks = []

        tasks = [
            loop.run_in_executor(
            self.pool_executor,
            Forecast.run_forecast_backlog,
            self.backlog_min,
            self.backlog_max,
            throughput_forecast,
            )
            for _ in range(self.nr_simulations)
        ]

        forecast_weeks = await asyncio.gather(*tasks)
    
        return forecast_weeks
    
    @staticmethod
    def run_forecast_backlog(backlog_min: int,backlog_max: int,throughput_forecast: List[int]) -> int:
        
        backlog_done = 0
        forecast_backlog = 0
        backlog = np.random.randint(backlog_min, backlog_max + 1)

        while backlog_done < backlog:
            random_throughput = int(np.random.choice(throughput_forecast))
            backlog_done += random_throughput
            forecast_backlog += 1
        
        return forecast_backlog

    @staticmethod
    def calculate_percentiles(forecast_weeks:List[int],percentiles:List[int]) -> dict:

        if len(forecast_weeks) == 0 or len(percentiles) == 0:
            raise ValueError("Os argumentos não podem vir vazios.Não é possível calcular os percentis.")
    
        return {p: int(np.percentile(forecast_weeks, p)) for p in percentiles}

    def format_forecast_response(self, throughput_forecast: List[int], p50:int, p75:int, p85:int, p95:int) -> dict:


        return {
        
            'Backlog-min': self.backlog_min,
            'Backlog-max':self.backlog_max,
            'Throughput-Forecast': throughput_forecast,
            'Simulations':self.nr_simulations,
            'Percentil-50':p50,
            'Percentil-75':p75,
            'Percentil-85':p85,
            'Percentil-95':p95

        }

    









