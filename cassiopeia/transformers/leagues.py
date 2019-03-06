from typing import Type, TypeVar
from copy import deepcopy

from datapipelines import DataTransformer, PipelineContext

from ..core.league import LeaguePositionData, LeaguePositionsData, LeagueEntry, LeagueEntries, LeaguesListData, LeagueListData, SummonerLeagues, League, ChallengerLeagueListData, ChallengerLeague, GrandmasterLeagueListData, GrandmasterLeague, MasterLeagueListData, MasterLeague, PositionalLeaguesListData, PositionalQueuesData

from ..dto.league import LeaguesListDto, LeagueListDto, ChallengerLeagueListDto, GrandmasterLeagueListDto, MasterLeagueListDto, LeaguePositionDto, LeaguePositionsDto, PositionalLeaguesListDto, PositionalQueuesDto

T = TypeVar("T")
F = TypeVar("F")


class LeagueTransformer(DataTransformer):
    @DataTransformer.dispatch
    def transform(self, target_type: Type[T], value: F, context: PipelineContext = None) -> T:
        pass

    # Dto to Data

    @transform.register(PositionalQueuesDto, PositionalQueuesData)
    def league_positional_queues_dto_to_data(self, value: PositionalQueuesDto, context: PipelineContext = None) -> PositionalQueuesData:
        return PositionalQueuesData([queue for queue in value["queues"]], region=value["region"])

    @transform.register(LeaguePositionDto, LeaguePositionData)
    def league_position_dto_to_data(self, value: LeaguePositionDto, context: PipelineContext = None) -> LeaguePositionData:
        return LeaguePositionData(**value)

    @transform.register(LeaguePositionsDto, LeaguePositionsData)
    def league_positions_dto_to_data(self, value: LeaguePositionsDto, context: PipelineContext = None) -> LeaguePositionsData:
        data = deepcopy(value)
        data = [LeagueTransformer.league_position_dto_to_data(self, league) for league in data["positions"]]
        return LeaguePositionsData(data, summoner_id=value["summonerId"], region=value["region"])

    @transform.register(LeagueListDto, LeagueListData)
    def league_list_dto_to_data(self, value: LeagueListDto, context: PipelineContext = None) -> LeagueListData:
        return LeagueListData(**value)

    @transform.register(LeaguesListDto, LeaguesListData)
    def leagues_list_dto_to_data(self, value: LeaguesListDto, context: PipelineContext = None) -> LeaguesListData:
        data = deepcopy(value)
        for league in data["leagues"]:
            league["region"] = data["region"]
            league["summonerId"] = data["summonerId"]
            for entry in league["entries"]:
                entry["tier"] = league["tier"]
                entry["leagueName"] = league["name"]
                entry["queueType"] = league["queue"]
                entry["region"] = league["region"]
        data = [LeagueTransformer.league_list_dto_to_data(self, league) for league in data["leagues"]]
        return LeaguesListData(data, summoner_id=value["summonerId"], region=value["region"])

    @transform.register(PositionalLeaguesListDto, PositionalLeaguesListData)
    def league_positions_list_dto_to_data(self, value: PositionalLeaguesListDto, context: PipelineContext = None) -> PositionalLeaguesListData:
        kwargs = {
            "region": value["region"],
            "queue": value["queue"],
            "tier": value["tier"],
            "division": value["division"],
            "position": value["position"],
            "page": value["page"]
        }
        return PositionalLeaguesListData([self.league_position_dto_to_data(entry) for entry in value["entries"]], **kwargs)

    @transform.register(ChallengerLeagueListDto, ChallengerLeagueListData)
    def challenger_league_list_dto_to_data(self, value: ChallengerLeagueListDto, context: PipelineContext = None) -> ChallengerLeagueListData:
        return ChallengerLeagueListData(**value)

    @transform.register(GrandmasterLeagueListDto, GrandmasterLeagueListData)
    def grandmaster_league_list_dto_to_data(self, value: GrandmasterLeagueListDto, context: PipelineContext = None) -> GrandmasterLeagueListData:
        return GrandmasterLeagueListData(**value)

    @transform.register(MasterLeagueListDto, MasterLeagueListData)
    def master_league_list_dto_to_data(self, value: MasterLeagueListDto, context: PipelineContext = None) -> MasterLeagueListData:
        return MasterLeagueListData(**value)

    # Data to Core

    @transform.register(LeaguePositionData, LeagueEntry)
    def league_position_data_to_core(self, value: LeaguePositionData, context: PipelineContext = None) -> LeagueEntry:
        data = deepcopy(value)
        return LeagueEntry.from_data(data)

    #@transform.register(LeaguePositionsData, LeagueEntries)
    def league_positions_data_to_core(self, value: LeaguePositionsData, context: PipelineContext = None) -> LeagueEntries:
        data = deepcopy(value)
        return LeagueEntries.from_data(*[LeagueTransformer.league_position_data_to_core(self, position) for position in data], summoner=value.summoner_id, region=value.region)

    #@transform.register(LeagueListData, League)
    def league_list_data_to_core(self, value: LeagueListData, context: PipelineContext = None) -> League:
        data = deepcopy(value)
        return League.from_data(data)

    @transform.register(LeaguesListData, SummonerLeagues)
    def leagues_list_data_to_core(self, value: LeaguesListData, context: PipelineContext = None) -> SummonerLeagues:
        return SummonerLeagues(*[LeagueTransformer.league_list_data_to_core(self, league) for league in value])

    #@transform.register(ChallengerLeagueListData, ChallengerLeague)
    def challenger_league_list_data_to_core(self, value: ChallengerLeagueListData, context: PipelineContext = None) -> ChallengerLeague:
        data = deepcopy(value)
        return ChallengerLeague.from_data(data)

    #@transform.register(GrandmasterLeagueListData, GrandmasterLeague)
    def grandmaster_league_list_data_to_core(self, value: GrandmasterLeagueListData, context: PipelineContext = None) -> GrandmasterLeague:
        data = deepcopy(value)
        return GrandmasterLeague.from_data(data)

    #@transform.register(MasterLeagueListData, MasterLeague)
    def master_league_list_data_to_core(self, value: MasterLeagueListData, context: PipelineContext = None) -> MasterLeague:
        data = deepcopy(value)
        return MasterLeague.from_data(data)
