import sublime
import sublime_plugin
from typing import List, Optional


EXPERIMENTAL_PHANTOMS = True

#region EXPERIMENTAL_PHANTOMS
REND_PHANTOM_SET_MAP = {}
def get_phantom_set(view: sublime.View):
	global REND_PHANTOM_SET_MAP
	id = view.buffer_id()
	phantom_set_key = "rend_phantom_set"
	phantom_set = REND_PHANTOM_SET_MAP.get(id)
	if phantom_set is None:
		REND_PHANTOM_SET_MAP[id] = sublime.PhantomSet(view, phantom_set_key)
	return REND_PHANTOM_SET_MAP[id]
#endregion


class Marker:
	def __init__(self, view: sublime.View, region: sublime.Region) -> None:
		self.view: sublime.View = view
		self.region = region
		#region EXPERIMENTAL_PHANTOMS
		fold_start = region.begin() if EXPERIMENTAL_PHANTOMS else view.line(region.begin()).end()
		#endregion
		self.fold_region = sublime.Region(fold_start, region.end())

	def fold(self):
		self.view.fold(self.fold_region)

	def unfold(self):
		self.view.unfold(self.fold_region)

	def is_folded(self):
		return self.view.is_folded(self.region)

	def is_at_comment(self, point: int):
		first_line = self.view.line(self.region.begin())
		end_line = self.view.line(self.region.end())
		return first_line.contains(point) or end_line.contains(point)

	def contains(self, region: sublime.Region):
		return self.region.contains(region)

	#region EXPERIMENTAL_PHANTOMS
	def phantom(self):
		text = self.view.substr(self.view.find(r'\W+.*+\n', self.region.begin())).strip()
		command = sublime.command_url('rend_unfold', {'point': self.region.begin()})
		comment_region = self.view.expand_to_scope(self.region.begin(), 'comment')
		phantom_start = comment_region if comment_region else self.region
		return sublime.Phantom(
			phantom_start,
			f'''<a href="{command}"
				style="display: block; text-decoration: none; padding: 0 0.4rem; border: 1px solid color(var(--foreground) alpha(0.25)); color: color(var(--foreground) alpha(0.75))">
				{text}
			</a>''',
			sublime.LAYOUT_INLINE
		)
	#endregion


class FindEndRegions(sublime_plugin.ViewEventListener):
	def on_load(self) -> None:
		self.view.run_command('rend_fold_all')

class RendFoldAll(sublime_plugin.TextCommand):
	def run(self, _: sublime.Edit) -> None:
		#region EXPERIMENTAL_PHANTOMS
		phantoms: List[sublime.Phantom] = []
		#endregion
		marker_regions = find_marked_regions(self.view)
		markers = marker_regions_to_marker(self.view, marker_regions)
		for m in markers:
			m.fold()
			#region EXPERIMENTAL_PHANTOMS
			phantoms.append(m.phantom())
			#endregion
		#region EXPERIMENTAL_PHANTOMS
		if EXPERIMENTAL_PHANTOMS:
			phantom_set = get_phantom_set(self.view)
			phantom_set.update(phantoms)
		#endregion


class RendUnfoldAll(sublime_plugin.TextCommand):
	def run(self, _: sublime.Edit) -> None:
		#region EXPERIMENTAL_PHANTOMS
		phantoms: List[sublime.Phantom] = []
		#endregion
		marker_regions = find_marked_regions(self.view)
		markers = marker_regions_to_marker(self.view, marker_regions)
		for m in markers:
			m.unfold()
		#region EXPERIMENTAL_PHANTOMS
		if EXPERIMENTAL_PHANTOMS:
			phantom_set = get_phantom_set(self.view)
			phantom_set.update([])
		#endregion

class RendFold(sublime_plugin.TextCommand):
	def run(self, _: sublime.Edit) -> None:
		sel = self.view.sel()
		if not sel:
			return
		#region EXPERIMENTAL_PHANTOMS
		phantoms: List[sublime.Phantom] = []
		#endregion
		cursor = sel[0].b
		marker_regions = find_marked_regions(self.view)
		markers = marker_regions_to_marker(self.view, marker_regions)
		for m in markers:
			if m.is_at_comment(cursor):
				m.fold()
			#region EXPERIMENTAL_PHANTOMS
			if m.is_folded():
				phantoms.append(m.phantom())
			#endregion
		#region EXPERIMENTAL_PHANTOMS
		if EXPERIMENTAL_PHANTOMS:
			phantom_set = get_phantom_set(self.view)
			phantom_set.update(phantoms)
		#endregion


class RendUnfold(sublime_plugin.TextCommand):
	def run(self, _: sublime.Edit, point: Optional[int]=None) -> None:
		sel = self.view.sel()
		if not sel:
			return
		#region EXPERIMENTAL_PHANTOMS
		phantoms: List[sublime.Phantom] = []
		#endregion
		cursor = point or sel[0].b
		marker_regions = find_marked_regions(self.view)
		markers = marker_regions_to_marker(self.view, marker_regions)
		for i in range(len(markers)):
			marker = markers[i]
			if marker.is_at_comment(cursor):
				marker.unfold()
				print('marker', self.view.substr(marker.region))
				#region But Fold Inner Markers
				for inner_marker in markers[i+1:]:
					if marker.contains(inner_marker.region):
						inner_marker.fold()
				# endregion
			#region EXPERIMENTAL_PHANTOMS
			if marker.is_folded():
				phantoms.append(marker.phantom())
			#endregion
		#region EXPERIMENTAL_PHANTOMS
		if EXPERIMENTAL_PHANTOMS:
			phantom_set = get_phantom_set(self.view)
			phantom_set.update(phantoms)
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