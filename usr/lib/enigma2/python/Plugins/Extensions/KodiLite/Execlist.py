
def Execlist(session, index):
    if "WorldTv" in index:
        from plugins.WorldTvE2.WorldTvE2 import WorldTvE2
        session.open(WorldTvE2)
    elif "AdultTv" in index:
        from plugins.AdultTvE2.AdultTvE2 import AdultTvE2
        session.open(AdultTvE2)
    elif "TivuStream" in index:
        from plugins.TivuStreamE2.TivuStreamE2 import TivuStreamE2
        session.open(TivuStreamE2)
    elif "Tivu18" in index:
        from plugins.Tivu18E2.Tivu18 import Tivu18
        session.open(Tivu18)
