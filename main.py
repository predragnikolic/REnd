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

	def contains(self, point: int):
		return self.region.contains(point)


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
		markers = marker_regions_to_marker(self.view, marker_regions, cursor)
		for m in markers:
			if m.contains(cursor):
				m.fold()
				break

class RendUnfold(sublime_plugin.TextCommand):
	def run(self, _: sublime.Edit) -> None:
		sel = self.view.sel()
		if not sel:
			return
		cursor = sel[0].b
		marker_regions = find_marked_regions(self.view)
		markers = marker_regions_to_marker(self.view, marker_regions, cursor)
		for m in markers:
			if m.contains(cursor):
				m.unfold()
				break


def find_marked_regions(view: sublime.View) -> List[sublime.Region]:
	return list(filter(lambda r: view.match_selector(r.begin(), 'comment') , view.find_all(r"\bregion\b")))


def marker_regions_to_marker(view: sublime.View, marked_regions: List[sublime.Region], cursor_point: Optional[int] = None) -> List[Marker]:
	result: List[Marker] = []
	for i in range(len(marked_regions)):
		maybe_start_r = marked_regions[i]
		if cursor_point and maybe_start_r.begin() > cursor_point:
			# don't create markers past cursor point
			break
		start_word = view.substr(maybe_start_r)
		if start_word != 'region':
			continue
		maybe_end_r = view.find(r'\bendregion\b', maybe_start_r.begin())
		end_word = view.substr(maybe_end_r)
		if end_word != 'endregion':
			continue
		result.append(
			Marker(
				view, sublime.Region(maybe_start_r.begin(), maybe_end_r.end())
		   )
		)
	return result