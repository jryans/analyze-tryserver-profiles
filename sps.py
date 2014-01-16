import json

def filter_measurements(profile, is_startup_test=False):
  startMeasurementMarker = "MEASUREMENT_START"
  stopMeasurementMarker = "MEASUREMENT_STOP"
  samples = profile["threads"][0]["samples"]
  measured_samples = []
  in_measurement = is_startup_test
  for sample in samples:
    if "marker" in sample:
      for marker in sample["marker"]:
        if startMeasurementMarker in marker["name"]:
          in_measurement = True
        if stopMeasurementMarker in marker["name"]:
          in_measurement = False
    if in_measurement:
      measured_samples.append(sample)
  profile["threads"][0]["samples"] = measured_samples
  return profile

def merge_profiles(profiles):
  first_profile = profiles[0]
  other_profiles = profiles[1:]
  first_samples = first_profile["threads"][0]["samples"]
  for other_profile in other_profiles:
    other_samples = other_profile["threads"][0]["samples"]
    first_samples.extend(other_samples)
  return first_profile

def compress_profile(profile):
  symbols = set()
  for thread in profile["threads"]:
    for sample in thread["samples"]:
      for frame in sample["frames"]:
        if isinstance(frame, basestring):
          symbols.add(frame)
        else:
          symbols.add(frame["location"])
  location_to_index = dict((l, str(i)) for i, l in enumerate(symbols))
  for thread in profile["threads"]:
    for sample in thread["samples"]:
      for i, frame in enumerate(sample["frames"]):
        if isinstance(frame, basestring):
          sample["frames"][i] = location_to_index[frame]
        else:
          frame["location"] = location_to_index[frame["location"]]
  profile["format"] = "profileJSONWithSymbolicationTable,1"
  profile["symbolicationTable"] = dict(enumerate(symbols))
  profile["profileJSON"] = { "threads": profile["threads"] }
  del profile["threads"]

def save_profile(profile, filename):
  f = open(filename, "w")
  json.dump(profile, f)
  f.close()
