import sublime
import sublime_plugin
from typing import List, Optional


class Marker:
	def __init__(self, view: sublime.View, region: sublime.Region) -> None:
		self.view: sublime.View = view
		self.region = region
		end_of_first_line = view.line(region.begin()).end()
		self.fold_region = sublime.Region(end_of_first_line, region.end())

	def fold(self):
		self.view.fold(self.fold_region)

	def unfold(self):
		self.view.unfold(self.fold_region)

	def is_at_comment(self, point: int):
		first_line = self.view.line(self.region.begin())
		end_line = self.view.line(self.region.end())
		return first_line.contains(point) or end_line.contains(point)

	def contains(self, region: sublime.Region):
		return self.region.contains(region)


class FindEndRegions(sublime_plugin.ViewEventListener):
	def on_load(self) -> None:
		self.view.run_command('rend_fold_all')


class RendFoldAll(sublime_plugin.TextCommand):
	def run(self, _: sublime.Edit) -> None:
		marker_regions = find_marked_regions(self.view)
		markers = marker_regions_to_marker(self.view, marker_regions)
		for m in markers:
			m.fold()


class RendUnfoldAll(sublime_plugin.TextCommand):
	def run(self, _: sublime.Edit) -> None:
		marker_regions = find_marked_regions(self.view)
		markers = marker_regions_to_marker(self.view, marker_regions)
		for m in markers:
			m.unfold()


class RendFold(sublime_plugin.TextCommand):
	def run(self, _: sublime.Edit) -> None:
		sel = self.view.sel()
		if not sel:
			return
		cursor = sel[0].b
		marker_regions = find_marked_regions(self.view)
		markers = marker_regions_to_marker(self.view, marker_regions)
		for m in markers:
			if m.is_at_comment(cursor):
				m.fold()
				break


class RendUnfold(sublime_plugin.TextCommand):
	def run(self, _: sublime.Edit) -> None:
		sel = self.view.sel()
		if not sel:
			return
		cursor = sel[0].b
		marker_regions = find_marked_regions(self.view)
		markers = marker_regions_to_marker(self.view, marker_regions)
		for i in range(len(markers)):
			marker = markers[i]
			if marker.is_at_comment(cursor):
				marker.unfold()
				#region But Fold Inner Markers
				for inner_marker in markers[i+1:]:
					if marker.contains(inner_marker.region):
						inner_marker.fold()
				#endregion


def find_marked_regions(view: sublime.View) -> List[sublime.Region]:
	return list(filter(lambda r: view.match_selector(r.begin(), 'comment') , view.find_all(r'(end)?region')))


def marker_regions_to_marker(view: sublime.View, marked_regions: List[sublime.Region]) -> List[Marker]:
	result: List[Marker] = []
	for i in range(len(marked_regions)):
		maybe_start_r = marked_regions[i]
		start_word = view.substr(maybe_start_r)
		if start_word != 'region':
			continue

		end_region = None
		#region Find End Region
		skip = 0
		for r in marked_regions[i+1:]:
			end_word = view.substr(r)
			if end_word == 'region':
				skip += 1
			if end_word == 'endregion':
				skip -= 1
			if skip == -1:
				end_region = r
				break
		#endregion
		if not end_region:
			continue
		result.append(
			Marker(view, sublime.Region(maybe_start_r.begin(), end_region.end()))
		)
	return result